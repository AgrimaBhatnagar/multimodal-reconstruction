from pathlib import Path
import json
import yaml

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_json(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=float)

def find_images(folder):
    exts = {".jpg",".jpeg",".png",".JPG",".JPEG",".PNG"}
    return sorted(p for p in Path(folder).iterdir() if p.suffix in exts)
