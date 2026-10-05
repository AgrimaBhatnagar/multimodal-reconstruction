from pathlib import Path
import numpy as np
import pandas as pd
import cv2
from scipy.spatial.transform import Rotation
import open3d as o3d


def load_intrinsics(path):
    arr = pd.read_csv(path, header=None).values.astype(float)

    if arr.shape == (3, 3):
        return arr

    df = pd.read_csv(path)
    vals = df.values.astype(float).reshape(-1)

    if len(vals) >= 9:
        return vals[:9].reshape(3, 3)

    raise ValueError("Cannot parse camera_matrix.csv")


def load_odometry(path):
    df = pd.read_csv(path, skipinitialspace=True)
    df.columns = [str(c).strip() for c in df.columns]

    required = [
        "frame",
        "x",
        "y",
        "z",
        "qx",
        "qy",
        "qz",
        "qw",
    ]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing odometry columns: {missing}")

    return df


def pose_matrix(row):
    """
    Supplied odometry is treated as a world-to-camera pose.

    Camera-frame depth is converted to world coordinates with:

        p_world = R.T @ (p_camera - t)
    """
    R = Rotation.from_quat(
        [
            row.qx,
            row.qy,
            row.qz,
            row.qw,
        ]
    ).as_matrix()

    t = np.array(
        [
            row.x,
            row.y,
            row.z,
        ],
        dtype=float,
    )

    T = np.eye(4)

    T[:3, :3] = R.T
    T[:3, 3] = -R.T @ t

    return T


def depth_to_points(
    depth,
    K,
    scale=0.001,
    confidence=None,
    min_depth=0.1,
    max_depth=8.0,
):
    z = depth.astype(np.float32) * scale

    ys, xs = np.indices(z.shape)

    valid = (
        np.isfinite(z)
        & (z >= min_depth)
        & (z <= max_depth)
    )

    if confidence is not None:
        valid &= confidence > 0

    fx = K[0, 0]
    fy = K[1, 1]
    cx = K[0, 2]
    cy = K[1, 2]

    x = (xs - cx) * z / fx
    y = (ys - cy) * z / fy

    return np.column_stack(
        (
            x[valid],
            y[valid],
            z[valid],
        )
    ).astype(np.float32)


def _to_pcd(points, voxel):
    pcd = o3d.geometry.PointCloud()
    if len(points):
        pcd.points = o3d.utility.Vector3dVector(
            np.asarray(points, dtype=np.float64)
        )
        if voxel:
            pcd = pcd.voxel_down_sample(float(voxel))
    return pcd


def _refine_against_previous(
    current_world,
    previous_world,
    voxel=0.06,
    max_correspondence=0.12,
    max_iteration=30,
):
    """
    Perform a bounded local ICP correction in world coordinates.

    The correction is applied only to the current keyframe. It is not
    propagated as a new global pose, which limits drift amplification.
    """
    source = _to_pcd(current_world, voxel)
    target = _to_pcd(previous_world, voxel)

    if len(source.points) < 50 or len(target.points) < 50:
        return current_world, {
            "accepted": False,
            "fitness": 0.0,
            "rmse": None,
        }

    result = o3d.pipelines.registration.registration_icp(
        source,
        target,
        max_correspondence,
        np.eye(4),
        o3d.pipelines.registration.TransformationEstimationPointToPoint(),
        o3d.pipelines.registration.ICPConvergenceCriteria(
            relative_fitness=1e-6,
            relative_rmse=1e-6,
            max_iteration=max_iteration,
        ),
    )

    fitness = float(result.fitness)
    rmse = float(result.inlier_rmse) if result.inlier_rmse else None

    # Conservative acceptance rule.  The thresholds are deliberately
    # recorded as metadata rather than presented as benchmark accuracy.
    accepted = (
        fitness >= 0.30
        and rmse is not None
        and rmse <= 0.08
    )

    if not accepted:
        return current_world, {
            "accepted": False,
            "fitness": fitness,
            "rmse": rmse,
        }

    T = np.asarray(result.transformation, dtype=float)
    pts_h = np.c_[
        current_world,
        np.ones(len(current_world)),
    ]

    corrected = (
        T @ pts_h.T
    ).T[:, :3]

    return corrected, {
        "accepted": True,
        "fitness": fitness,
        "rmse": rmse,
    }


def reconstruct(
    capture_dir,
    voxel=0.03,
    confidence_min=1,
    max_frames=None,
    refine_registration=True,
    registration_stride=10,
):
    d = Path(capture_dir)

    K = load_intrinsics(
        d / "camera_matrix.csv"
    )

    odo = load_odometry(
        d / "odometry.csv"
    )

    depth_files = sorted(
        (d / "depth").glob("*.png")
    )

    conf_files = sorted(
        (d / "confidence").glob("*.png")
    )

    conf_by_name = {
        p.name: p
        for p in conf_files
    }

    pcd = o3d.geometry.PointCloud()

    limit = (
        len(depth_files)
        if max_frames is None
        else min(
            max_frames,
            len(depth_files),
        )
    )

    previous_keyframe = None
    accepted_refinements = 0
    attempted_refinements = 0
    fitness_values = []
    rmse_values = []

    for local_idx, dp in enumerate(depth_files[:limit]):
        cf = conf_by_name.get(dp.name)

        depth = cv2.imread(
            str(dp),
            cv2.IMREAD_UNCHANGED,
        )

        conf = (
            cv2.imread(
                str(cf),
                cv2.IMREAD_UNCHANGED,
            )
            if cf
            else None
        )

        pts = depth_to_points(
            depth,
            K,
            confidence=conf,
        )

        if len(pts) == 0:
            continue

        frame = int(dp.stem)

        row = odo.iloc[
            min(
                frame,
                len(odo) - 1,
            )
        ]

        T = pose_matrix(row)

        pts_h = np.c_[
            pts,
            np.ones(len(pts)),
        ]

        world = (
            T @ pts_h.T
        ).T[:, :3]

        is_keyframe = (
            registration_stride > 0
            and local_idx % registration_stride == 0
        )

        if (
            refine_registration
            and is_keyframe
            and previous_keyframe is not None
        ):
            attempted_refinements += 1

            world, reg = _refine_against_previous(
                world,
                previous_keyframe,
            )

            if reg["fitness"] > 0:
                fitness_values.append(
                    reg["fitness"]
                )

            if reg["rmse"] is not None:
                rmse_values.append(
                    reg["rmse"]
                )

            if reg["accepted"]:
                accepted_refinements += 1

        if is_keyframe:
            previous_keyframe = world.copy()

        pcd.points.extend(
            o3d.utility.Vector3dVector(
                world
            )
        )

    if voxel and len(pcd.points):
        pcd = pcd.voxel_down_sample(
            voxel
        )

    registration_meta = {
        "enabled": bool(refine_registration),
        "stride": int(registration_stride),
        "attempted": int(attempted_refinements),
        "accepted": int(accepted_refinements),
        "acceptance_fitness_threshold": 0.30,
        "acceptance_rmse_threshold_m": 0.08,
        "mean_fitness": (
            float(np.mean(fitness_values))
            if fitness_values
            else None
        ),
        "mean_rmse_m": (
            float(np.mean(rmse_values))
            if rmse_values
            else None
        ),
    }

    return pcd, {
        "frames": limit,
        "source_points": len(pcd.points),
        "K": K.tolist(),
        "pose_convention": "world_to_camera_inverted",
        "registration_refinement": registration_meta,
    }


def pcd_numpy(pcd):
    return np.asarray(
        pcd.points
    )


def save_ply(pcd, path):
    Path(path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    o3d.io.write_point_cloud(
        str(path),
        pcd,
    )
