import math

def ci(value, relative=0.02, absolute=0.01, level=0.95):
    half=max(abs(value)*relative,absolute)
    return {"value":float(value),"lower":float(value-half),"upper":float(value+half),
            "half_width":float(half),"confidence_level":level}

def wall_measurement(length, tier):
    rel={"lidar":0.01,"video":0.03,"photos":0.08}.get(tier,0.10)
    return ci(length,relative=rel)

def scalar_measurement(value,tier,absolute=0.01):
    rel={"lidar":0.01,"video":0.03,"photos":0.08}.get(tier,0.10)
    return ci(value,relative=rel,absolute=absolute)
