from pathlib import Path
import time, cv2, numpy as np

from .capture import validate_capture
from .lidar import reconstruct, pcd_numpy
from .geometry import floor_ceiling, xy_hull, wall_segments
from .openings import detect_openings_from_wall_projection
from .measurements import scalar_measurement, wall_measurement
from .damage import detect_surface_damage, concealed_damage_flags
from .photo_video import (
    inventory_photos,
    extract_video_frames,
    reconstruct_from_images,
)
from .stitching import stitch_rooms
from .rendering import render_room
from .io_utils import save_json, find_images


def geometry_from_points(pts, tier):
    if len(pts) < 20:
        return {
            "floor_area_m2": scalar_measurement(0.0, tier),
            "ceiling_height_m": scalar_measurement(0.0, tier),
            "walls": [],
            "openings": [],
            "centroid": [0.0, 0.0],
            "floor_z_m": 0.0,
            "ceiling_z_m": 0.0,
            "geometry_status": "INSUFFICIENT_3D_POINTS",
        }

    try:
        floor, ceil, height = floor_ceiling(pts)
        hull, area, per = xy_hull(pts)
        walls = wall_segments(pts)

        try:
            openings = detect_openings_from_wall_projection(pts, walls)
        except Exception:
            openings = []

        geometry_status = (
            "METRIC_GEOMETRY"
            if tier == "lidar"
            else "PROVISIONAL_RELATIVE_SCALE"
        )

        return {
            "floor_area_m2": scalar_measurement(
                float(area), tier, absolute=0.05
            ),
            "ceiling_height_m": scalar_measurement(
                float(height), tier, absolute=0.015
            ),
            "walls": [
                {
                    **w,
                    "measurement": wall_measurement(
                        w["length_m"], tier
                    ),
                }
                for w in walls
            ],
            "openings": [
                {
                    **o,
                    "measurement": scalar_measurement(
                        o["width_m"], tier, absolute=0.02
                    ),
                }
                for o in openings
            ],
            "centroid": pts[:, :2].mean(axis=0).tolist(),
            "floor_z_m": float(floor),
            "ceiling_z_m": float(ceil),
            "geometry_status": geometry_status,
        }

    except Exception as exc:
        return {
            "floor_area_m2": scalar_measurement(0.0, tier),
            "ceiling_height_m": scalar_measurement(0.0, tier),
            "walls": [],
            "openings": [],
            "centroid": pts[:, :2].mean(axis=0).tolist(),
            "geometry_status": "GEOMETRY_EXTRACTION_FAILED",
            "geometry_error": str(exc),
        }


def build_lidar(capture_dir, tier, output_dir, name):
    start = time.perf_counter()

    pcd, meta = reconstruct(capture_dir)
    pts = pcd_numpy(pcd)

    if len(pts) < 3:
        raise RuntimeError("No usable 3-D points")

    geometry = geometry_from_points(pts, tier)

    room = {
        "room_id": name,
        "tier": tier,
        **geometry,
    }

    room["surface_damage"] = []
    room["concealed_damage"] = concealed_damage_flags([])

    room["scope"] = [
        {
            "line_item": "room_measurement",
            "quantity": 1,
            "unit": "room",
            "confidence": 0.8,
        },
        {
            "line_item": "floor_area",
            "quantity": float(
                geometry["floor_area_m2"]["value"]
            ),
            "unit": "m2",
            "confidence": 0.8,
        },
    ]

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    render_room(
        room,
        out / f"{name}_plan.png"
    )

    result = {
        "schema_version": "1.0",
        "property_id": name,
        "rooms": [room],
        "adjacency": [],
        "measurements": [],
        "damage": [],
        "scope": room["scope"],
        "run": {
            "tier": tier,
            "seconds": time.perf_counter() - start,
            "source_points": len(pts),
            **meta,
        },
    }

    save_json(result, out / f"{name}.json")

    return result


def build_photos(capture_dir, tier, output_dir, name):
    start = time.perf_counter()

    inv = inventory_photos(capture_dir)
    imgs = find_images(capture_dir)

    if not inv["valid_2_to_8"]:
        raise ValueError(
            "Photo tier requires 2 to 8 images per room"
        )

    pts, reconstruction_meta = reconstruct_from_images(imgs)

    geometry = geometry_from_points(pts, tier)

    damage = []

    for image_path in imgs:
        img = cv2.imread(str(image_path))

        if img is not None:
            damage.extend(
                detect_surface_damage(img)
            )

    room = {
        "room_id": name,
        "tier": tier,
        **geometry,
        "surface_damage": damage,
        "concealed_damage": concealed_damage_flags(damage),
        "scope": [
            {
                "line_item": "visual_surface_review",
                "quantity": 1,
                "unit": "room",
                "confidence": 0.5,
            }
        ],
    }

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    render_room(
        room,
        out / f"{name}_plan.png"
    )

    result = {
        "schema_version": "1.0",
        "property_id": name,
        "rooms": [room],
        "adjacency": [],
        "measurements": [],
        "damage": damage,
        "scope": room["scope"],
        "run": {
            "tier": tier,
            "seconds": time.perf_counter() - start,
            **inv,
            **reconstruction_meta,
        },
    }

    save_json(
        result,
        out / f"{name}.json"
    )

    return result


def build_video(capture_dir, tier, output_dir, name):
    start = time.perf_counter()

    p = Path(capture_dir)
    video = p if p.is_file() else p / "rgb.mp4"

    frames_dir = (
        Path(output_dir)
        / f"{name}_frames"
    )

    meta = extract_video_frames(
        video,
        frames_dir,
        stride=30,
    )

    frame_paths = find_images(frames_dir)

    if len(frame_paths) > 8:
        indices = np.linspace(
            0,
            len(frame_paths) - 1,
            8,
            dtype=int,
        )
        frame_paths = [
            frame_paths[i]
            for i in indices
        ]

    pts, reconstruction_meta = reconstruct_from_images(
        frame_paths
    )

    geometry = geometry_from_points(
        pts,
        tier,
    )

    damage = []

    for image_path in frame_paths:
        img = cv2.imread(str(image_path))

        if img is not None:
            damage.extend(
                detect_surface_damage(img)
            )

    room = {
        "room_id": name,
        "tier": tier,
        **geometry,
        "surface_damage": damage,
        "concealed_damage": concealed_damage_flags(damage),
        "scope": [
            {
                "line_item": "walkthrough_review",
                "quantity": 1,
                "unit": "room",
                "confidence": 0.5,
            }
        ],
    }

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    render_room(
        room,
        out / f"{name}_plan.png"
    )

    result = {
        "schema_version": "1.0",
        "property_id": name,
        "rooms": [room],
        "adjacency": [],
        "measurements": [],
        "damage": damage,
        "scope": room["scope"],
        "run": {
            "tier": tier,
            "seconds": time.perf_counter() - start,
            **meta,
            **reconstruction_meta,
        },
    }

    save_json(
        result,
        out / f"{name}.json"
    )

    return result
