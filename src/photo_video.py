from pathlib import Path
import cv2
import numpy as np
from .io_utils import find_images

def inventory_photos(folder):
    ims=find_images(folder)
    return {"count":len(ims),"files":[p.name for p in ims],
            "valid_2_to_8":2<=len(ims)<=8}

def extract_video_frames(video, out_dir, stride=30):
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    cap=cv2.VideoCapture(str(video))
    if not cap.isOpened(): raise ValueError(f"Cannot open {video}")
    i=0; saved=0
    while True:
        ok,frame=cap.read()
        if not ok: break
        if i%stride==0:
            cv2.imwrite(str(out/f"{i:06d}.jpg"),frame)
            saved+=1
        i+=1
    cap.release()
    return {"frames_read":i,"frames_saved":saved}

def video_metadata(video):
    cap=cv2.VideoCapture(str(video))
    if not cap.isOpened(): raise ValueError(f"Cannot open {video}")
    return {"width":int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height":int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps":float(cap.get(cv2.CAP_PROP_FPS)),
            "frames":int(cap.get(cv2.CAP_PROP_FRAME_COUNT))}
