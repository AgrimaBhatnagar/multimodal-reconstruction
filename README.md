# Multimodal Reconstruction - Applied AI Engineer Case Study

A local, reproducible engineering system for consumer-capture indoor reconstruction.

## Overview

This repository implements a multimodal indoor reconstruction pipeline designed around three consumer capture tiers:

1. Photos
2. Handheld video
3. LiDAR

Each tier is processed locally and converted into a canonical property representation. The system includes capture validation, reconstruction, geometry estimation, damage detection, uncertainty reporting, rendering, benchmarking, and evaluation tooling.

The repository is designed to be reproducible and to distinguish verified physical measurements from provisional or unavailable benchmark results.

---

## Implemented Capabilities

The current system includes:

- Photo capture validation
- Handheld video capture processing
- LiDAR/depth capture processing
- Camera and capture metadata handling
- Feature-based multi-view reconstruction for photos
- Video frame extraction and reconstruction
- Point-cloud processing
- Floor and ceiling estimation
- Wall geometry estimation
- Opening detection framework
- Surface damage detection
- Damage classification
- Concealed-damage flagging
- Scope line-item generation
- Measurement uncertainty representation
- Multi-room stitching representation
- Adjacency representation
- JSON output generation
- JSON schema validation
- Rendered floor-plan output
- Benchmark gate evaluation
- Repeatability evaluation
- Calibration checks
- Drift-accounting framework
- Consumer-application comparison framework
- Fix-loop reporting
- Local reproducibility tooling

---

## Input Tiers

### 1. Photos

The photo pipeline accepts 2-8 still images for a room.

Expected formats:

- JPG
- JPEG
- PNG

Example:

```powershell
python run.py --capture PHOTO_DIRECTORY --tier photos --name room_photos
