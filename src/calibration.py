import numpy as np

def absolute_errors(pred, gt):
    p=np.asarray(pred,float); g=np.asarray(gt,float)
    return np.abs(p-g)

def evaluate(pred,gt,tolerance):
    e=absolute_errors(pred,gt)
    return {"n":int(len(e)),
            "mean_abs_error":float(e.mean()) if len(e) else None,
            "max_abs_error":float(e.max()) if len(e) else None,
            "pass_rate":float((e<=tolerance).mean()) if len(e) else None,
            "tolerance":float(tolerance)}

def calibration_by_tier(rows):
    out={}
    for r in rows:
        out.setdefault(r["tier"],[]).append(r)
    return {tier:{"n":len(rs),
                   "mean_abs_error":float(np.mean([x["abs_error"] for x in rs]))}
            for tier,rs in out.items()}
