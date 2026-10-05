# Fix Loop

## Failure

The main engineering failure identified during development was multi-frame LiDAR registration instability.

The baseline reconstruction used the supplied pose trajectory without local registration refinement.

## Root Cause Hypothesis

The supplied pose trajectory provides a global initialization, but local frame-to-frame registration error can accumulate across a long depth sequence.

A fully unconstrained global ICP correction could introduce a different failure mode by propagating a locally good but globally inconsistent transformation.

## Shipped Fix

A bounded local registration refinement was added to:

```text
src/lidar.py