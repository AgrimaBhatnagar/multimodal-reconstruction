from pathlib import Path
import time, cv2, numpy as np
from .capture import validate_capture
from .lidar import reconstruct, pcd_numpy
from .geometry import floor_ceiling, xy_hull, wall_segments
from .openings import detect_openings_from_wall_projection
from .measurements import scalar_measurement, wall_measurement
from .damage import detect_surface_damage, concealed_damage_flags
from .photo_video import inventory_photos, extract_video_frames
from .stitching import stitch_rooms
from .rendering import render_room
from .io_utils import save_json, find_images

def build_lidar(capture_dir, tier, output_dir, name):
    start=time.perf_counter()
    pcd,meta=reconstruct(capture_dir)
    pts=pcd_numpy(pcd)
    if len(pts)<3: raise RuntimeError("No usable 3-D points")
    floor,ceil,height=floor_ceiling(pts)
    hull,area,per=xy_hull(pts)
    walls=wall_segments(pts)
    openings=detect_openings_from_wall_projection(pts,walls)
    room={
        "room_id":name,
        "tier":tier,
        "floor_area_m2":scalar_measurement(area,tier,absolute=0.05),
        "ceiling_height_m":scalar_measurement(height,tier,absolute=0.015),
        "walls":[{**w,"measurement":wall_measurement(w["length_m"],tier)} for w in walls],
        "openings":[{**o,"measurement":scalar_measurement(o["width_m"],tier,absolute=0.02)} for o in openings],
        "centroid":pts[:,:2].mean(0).tolist(),
        "floor_z_m":floor,"ceiling_z_m":ceil,
    }
    room["surface_damage"]=[]
    room["concealed_damage"]=concealed_damage_flags([])
    room["scope"]=[
        {"line_item":"room_measurement","quantity":1,"unit":"room","confidence":0.8},
        {"line_item":"floor_area","quantity":area,"unit":"m2","confidence":0.8}
    ]
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    render_room(room,out/f"{name}_plan.png")
    result={"schema_version":"1.0","property_id":name,
            "rooms":[room],"adjacency":[],"measurements":[],
            "damage":[],"scope":room["scope"],
            "run":{"tier":tier,"seconds":time.perf_counter()-start,"source_points":len(pts),**meta}}
    save_json(result,out/f"{name}.json")
    return result

def build_photos(capture_dir,tier,output_dir,name):
    start=time.perf_counter()
    inv=inventory_photos(capture_dir)
    imgs=find_images(capture_dir)
    damage=[]
    if imgs:
        img=cv2.imread(str(imgs[0]))
        if img is not None:
            damage=detect_surface_damage(img)
    room={"room_id":name,"tier":tier,
          "floor_area_m2":scalar_measurement(0.0,tier),
          "ceiling_height_m":scalar_measurement(0.0,tier),
          "walls":[],"openings":[],"centroid":[0,0],
          "surface_damage":damage,
          "concealed_damage":concealed_damage_flags(damage),
          "scope":[{"line_item":"visual_surface_review","quantity":1,"unit":"room","confidence":0.5}]}
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    result={"schema_version":"1.0","property_id":name,"rooms":[room],
            "adjacency":[],"measurements":[],"damage":damage,
            "scope":room["scope"],"run":{"tier":tier,"seconds":time.perf_counter()-start,**inv}}
    save_json(result,out/f"{name}.json")
    return result

def build_video(capture_dir,tier,output_dir,name):
    p=Path(capture_dir)
    video=p if p.is_file() else p/"rgb.mp4"
    frames_dir=Path(output_dir)/f"{name}_frames"
    meta=extract_video_frames(video,frames_dir,stride=30)
    room={"room_id":name,"tier":tier,"floor_area_m2":scalar_measurement(0,tier),
          "ceiling_height_m":scalar_measurement(0,tier),"walls":[],"openings":[],
          "centroid":[0,0],"surface_damage":[],"concealed_damage":concealed_damage_flags([]),
          "scope":[{"line_item":"walkthrough_review","quantity":1,"unit":"room","confidence":0.5}]}
    result={"schema_version":"1.0","property_id":name,"rooms":[room],
            "adjacency":[],"measurements":[],"damage":[],"scope":room["scope"],
            "run":{"tier":tier,**meta}}
    save_json(result,Path(output_dir)/f"{name}.json")
    return result
