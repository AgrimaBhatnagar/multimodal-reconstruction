import cv2
import numpy as np

CLASSES=("crack","stain","surface_loss")

def classify_damage_mask(mask):
    area=int((mask>0).sum())
    if area<20:
        return None
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    regions=[]
    for c in contours:
        a=cv2.contourArea(c)
        if a<20: continue
        x,y,w,h=cv2.boundingRect(c)
        aspect=max(w,h)/max(1,min(w,h))
        cls="crack" if aspect>4 else ("stain" if a<5000 else "surface_loss")
        regions.append({"class":cls,"pixel_area":float(a),
                        "bbox":[int(x),int(y),int(w),int(h)],
                        "confidence":0.45})
    return regions

def detect_surface_damage(image):
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    blur=cv2.GaussianBlur(gray,(5,5),0)
    lap=cv2.Laplacian(blur,cv2.CV_32F)
    score=np.abs(lap)
    threshold=float(np.percentile(score,97))
    mask=(score>=threshold).astype(np.uint8)*255
    kernel=np.ones((3,3),np.uint8)
    mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel)
    return classify_damage_mask(mask) or []

def concealed_damage_flags(surface_regions, rules=None):
    rules=rules or {"min_regions":2,"min_confidence":0.4}
    eligible=[r for r in surface_regions if r.get("confidence",0)>=rules["min_confidence"]]
    flagged=len(eligible)>=rules["min_regions"]
    return [{"rule":"multiple_consistent_surface_anomalies",
             "flagged":flagged,
             "evidence_count":len(eligible),
             "confidence":0.4 if flagged else 0.1}]
