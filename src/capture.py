from pathlib import Path
from .photo_video import inventory_photos, video_metadata

def detect_tier(path):
    p=Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Capture path does not exist: {p}")
    if p.is_file() and p.suffix.lower()==".mp4": return "video"
    if (p/"depth").exists() and (p/"odometry.csv").exists(): return "lidar"
    if any(x.suffix.lower() in {".jpg",".jpeg",".png"} for x in p.iterdir()): return "photos"
    if (p/"rgb.mp4").exists(): return "video"
    raise ValueError(f"Could not infer capture tier from: {p}")

def validate_capture(path,tier):
    p=Path(path)
    if not p.exists():
        return {"tier":tier,"valid":False,"missing":[f"path does not exist: {p}"]}
    if tier=="lidar":
        req=["depth","confidence","odometry.csv","camera_matrix.csv"]
        return {"tier":tier,"valid":all((p/x).exists() for x in req),
                "missing":[x for x in req if not (p/x).exists()]}
    if tier=="photos":
        inv=inventory_photos(p)
        return {"tier":tier,"valid":inv["valid_2_to_8"],**inv}
    if tier=="video":
        video=p if p.is_file() else p/"rgb.mp4"
        return {"tier":tier,"valid":video.exists(),
                "metadata":video_metadata(video) if video.exists() else None}
    raise ValueError(tier)
