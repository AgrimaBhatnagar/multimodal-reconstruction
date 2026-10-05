from pathlib import Path
import cv2
import numpy as np
from .io_utils import find_images


def inventory_photos(folder):
    ims = find_images(folder)
    return {
        "count": len(ims),
        "files": [p.name for p in ims],
        "valid_2_to_8": 2 <= len(ims) <= 8,
    }


def extract_video_frames(video, out_dir, stride=30):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise ValueError(f"Cannot open {video}")

    i = 0
    saved = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if i % stride == 0:
            cv2.imwrite(str(out / f"{i:06d}.jpg"), frame)
            saved += 1

        i += 1

    cap.release()

    return {
        "frames_read": i,
        "frames_saved": saved,
    }


def video_metadata(video):
    cap = cv2.VideoCapture(str(video))

    if not cap.isOpened():
        raise ValueError(f"Cannot open {video}")

    result = {
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": float(cap.get(cv2.CAP_PROP_FPS)),
        "frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
    }

    cap.release()
    return result


def reconstruct_from_images(image_paths, max_features=2500):
    """
    Monocular multi-view reconstruction.

    Produces a sparse 3-D point cloud from overlapping images using:
      SIFT -> feature matching -> essential matrix -> camera poses
      -> triangulation.

    Important:
    Monocular reconstruction has arbitrary scale. Therefore the returned
    geometry is explicitly marked as relative-scale unless a metric scale
    reference is supplied.
    """

    paths = [Path(p) for p in image_paths]

    if len(paths) < 2:
        return np.empty((0, 3), dtype=np.float32), {
            "status": "INSUFFICIENT_VIEWS",
            "scale_status": "relative",
        }

    images = []

    for p in paths:
        img = cv2.imread(str(p))
        if img is not None:
            images.append(img)

    if len(images) < 2:
        return np.empty((0, 3), dtype=np.float32), {
            "status": "INSUFFICIENT_VALID_IMAGES",
            "scale_status": "relative",
        }

    gray = [cv2.cvtColor(x, cv2.COLOR_BGR2GRAY) for x in images]

    h, w = gray[0].shape

    # Approximate intrinsics from the image itself.
    # This is suitable for reconstruction smoke testing but is NOT
    # equivalent to device-calibrated intrinsics.
    focal = float(max(h, w))
    cx = w / 2.0
    cy = h / 2.0

    K = np.array(
        [
            [focal, 0.0, cx],
            [0.0, focal, cy],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )

    sift = cv2.SIFT_create(nfeatures=max_features)

    keypoints = []
    descriptors = []

    for img in gray:
        kp, des = sift.detectAndCompute(img, None)
        keypoints.append(kp)
        descriptors.append(des)

    points_3d = []

    # First camera at origin.
    R_global = np.eye(3)
    t_global = np.zeros((3, 1))

    for i in range(len(images) - 1):

        if descriptors[i] is None or descriptors[i + 1] is None:
            continue

        matcher = cv2.BFMatcher(cv2.NORM_L2)

        matches = matcher.knnMatch(
            descriptors[i],
            descriptors[i + 1],
            k=2,
        )

        good = []

        for pair in matches:
            if len(pair) != 2:
                continue

            m, n = pair

            if m.distance < 0.75 * n.distance:
                good.append(m)

        if len(good) < 8:
            continue

        pts1 = np.float64(
            [keypoints[i][m.queryIdx].pt for m in good]
        )

        pts2 = np.float64(
            [keypoints[i + 1][m.trainIdx].pt for m in good]
        )

        E, mask = cv2.findEssentialMat(
            pts1,
            pts2,
            K,
            method=cv2.RANSAC,
            prob=0.999,
            threshold=1.0,
        )

        if E is None:
            continue

        _, R, t, pose_mask = cv2.recoverPose(
            E,
            pts1,
            pts2,
            K,
        )

        valid = pose_mask.ravel() > 0

        pts1_valid = pts1[valid]
        pts2_valid = pts2[valid]

        if len(pts1_valid) < 8:
            continue

        P1 = K @ np.hstack(
            [R_global, t_global]
        )

        R_next = R @ R_global
        t_next = t + R @ t_global

        P2 = K @ np.hstack(
            [R_next, t_next]
        )

        homogeneous = cv2.triangulatePoints(
            P1,
            P2,
            pts1_valid.T,
            pts2_valid.T,
        )

        homogeneous /= np.maximum(
            np.abs(homogeneous[3:4]),
            1e-12,
        )

        xyz = homogeneous[:3].T

        finite = np.isfinite(xyz).all(axis=1)

        xyz = xyz[finite]

        if len(xyz):
            points_3d.append(xyz.astype(np.float32))

        R_global = R_next
        t_global = t_next

    if not points_3d:
        return np.empty((0, 3), dtype=np.float32), {
            "status": "RECONSTRUCTION_FAILED",
            "scale_status": "relative",
        }

    cloud = np.vstack(points_3d)

    # Remove extreme triangulation outliers.
    finite = np.isfinite(cloud).all(axis=1)
    cloud = cloud[finite]

    if len(cloud) > 20:
        center = np.median(cloud, axis=0)
        distance = np.linalg.norm(cloud - center, axis=1)

        cutoff = np.percentile(distance, 95)

        cloud = cloud[distance <= cutoff]

    return cloud, {
        "status": "OK",
        "scale_status": "relative",
        "intrinsics_source": "approximate_from_image",
        "images_used": len(images),
        "points_3d": int(len(cloud)),
        "feature_method": "SIFT",
        "pose_method": "essential_matrix_RANSAC",
        "metric_scale": False,
    }
