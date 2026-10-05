import numpy as np

def detect_openings_from_wall_projection(points, wall_segments):
    # Conservative candidate detector: identifies large gaps along each wall.
    # It intentionally emits candidates rather than pretending semantic certainty.
    xy=points[:,:2]
    out=[]
    for i,w in enumerate(wall_segments):
        a=np.array(w["start"]); b=np.array(w["end"])
        d=b-a; L=np.linalg.norm(d)
        if L<0.5: continue
        u=d/L
        t=(xy-a)@u
        t=t[(t>=0)&(t<=L)]
        if len(t)<20: continue
        hist,edges=np.histogram(t,bins=max(10,int(L/0.1)))
        gaps=[]
        for j,c in enumerate(hist):
            if c==0:
                gaps.append((edges[j],edges[j+1]))
        if gaps:
            # Merge nearby empty bins.
            cur=None
            merged=[]
            for g in gaps:
                if cur is None: cur=list(g)
                elif g[0]-cur[1] <= 0.12: cur[1]=g[1]
                else: merged.append(cur); cur=list(g)
            if cur: merged.append(cur)
            for g0,g1 in merged:
                width=g1-g0
                if 0.5<=width<=2.5:
                    out.append({"opening_id":f"wall{i}_opening{len(out)}",
                                "wall_index":i,"width_m":float(width),
                                "confidence":0.35})
    return out
