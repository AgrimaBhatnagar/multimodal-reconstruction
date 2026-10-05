from pathlib import Path
import numpy as np
import pandas as pd
import cv2
from scipy.spatial.transform import Rotation
import open3d as o3d

def load_intrinsics(path):
    arr = pd.read_csv(path, header=None).values.astype(float)
    if arr.shape == (3,3):
        return arr
    df = pd.read_csv(path)
    vals = df.values.astype(float).reshape(-1)
    if len(vals) >= 9:
        return vals[:9].reshape(3,3)
    raise ValueError("Cannot parse camera_matrix.csv")

def load_odometry(path):
    df = pd.read_csv(path, skipinitialspace=True)
    df.columns = [str(c).strip() for c in df.columns]
    required = ["frame","x","y","z","qx","qy","qz","qw"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing odometry columns: {missing}")
    return df

def pose_matrix(row):
    T = np.eye(4)
    T[:3,:3] = Rotation.from_quat([row.qx,row.qy,row.qz,row.qw]).as_matrix()
    T[:3,3] = [row.x,row.y,row.z]
    return T

def depth_to_points(depth, K, scale=0.001, confidence=None, min_depth=0.1, max_depth=8.0):
    z = depth.astype(np.float32) * scale
    ys, xs = np.indices(z.shape)
    valid = np.isfinite(z) & (z >= min_depth) & (z <= max_depth)
    if confidence is not None:
        valid &= confidence > 0
    fx, fy, cx, cy = K[0,0], K[1,1], K[0,2], K[1,2]
    x = (xs-cx)*z/fx
    y = (ys-cy)*z/fy
    return np.column_stack((x[valid],y[valid],z[valid])).astype(np.float32)

def reconstruct(capture_dir, voxel=0.03, confidence_min=1, max_frames=None):
    d = Path(capture_dir)
    K = load_intrinsics(d/"camera_matrix.csv")
    odo = load_odometry(d/"odometry.csv")
    depth_files = sorted((d/"depth").glob("*.png"))
    conf_files = sorted((d/"confidence").glob("*.png"))
    conf_by_name = {p.name:p for p in conf_files}
    pcd = o3d.geometry.PointCloud()
    limit = len(depth_files) if max_frames is None else min(max_frames,len(depth_files))
    for dp in depth_files[:limit]:
        cf = conf_by_name.get(dp.name)
        depth = cv2.imread(str(dp), cv2.IMREAD_UNCHANGED)
        conf = cv2.imread(str(cf), cv2.IMREAD_UNCHANGED) if cf else None
        pts = depth_to_points(depth, K, confidence=conf)
        if len(pts)==0:
            continue
        frame = int(dp.stem)
        row = odo.iloc[min(frame, len(odo)-1)]
        T = pose_matrix(row)
        pts_h = np.c_[pts, np.ones(len(pts))]
        world = (T @ pts_h.T).T[:,:3]
        pcd.points.extend(o3d.utility.Vector3dVector(world))
    if voxel and len(pcd.points):
        pcd = pcd.voxel_down_sample(voxel)
    return pcd, {"frames":limit, "source_points":len(pcd.points), "K":K.tolist()}

def pcd_numpy(pcd):
    return np.asarray(pcd.points)

def save_ply(pcd, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    o3d.io.write_point_cloud(str(path), pcd)
