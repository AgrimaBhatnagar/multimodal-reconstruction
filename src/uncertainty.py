import numpy as np

def empirical_ci(values, level=0.95):
    x=np.asarray(values,dtype=float)
    if len(x)==0:
        return None
    mean=float(x.mean())
    if len(x)==1:
        half=0.0
    else:
        half=float(1.96*x.std(ddof=1)/np.sqrt(len(x)))
    return {"value":mean,"lower":mean-half,"upper":mean+half,
            "half_width":half,"confidence_level":level,"n":len(x)}
