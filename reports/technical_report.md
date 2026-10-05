# Technical Report

## 1. Objective

The system is a local multimodal indoor-reconstruction pipeline for consumer capture.

It accepts:

- Photos
- Handheld video
- LiDAR/depth captures

and produces a common structured property representation containing room geometry, walls, openings, damage candidates, scope information, uncertainty, and rendered plans.

The implementation prioritizes reproducibility, explicit uncertainty, graceful failure, and separation of development evidence from physical benchmark accuracy.

---

## 2. System Architecture

```text
Consumer Capture
      |
      v
Capture Validation
      |
      +-------------------+
      |                   |
    Photos              Video              LiDAR
      |                   |                  |
      +-------------------+------------------+
                          |
                          v
                  Reconstruction
                          |
                          v
              Canonical Room Representation
                          |
          +---------------+----------------+
          |               |                |
       Geometry        Damage          Uncertainty
          |               |                |
          +---------------+----------------+
                          |
                          v
                  Property Representation
                          |
              +-----------+-----------+
              |                       |
            JSON                 Rendered Plan
              |
              v
        Benchmark Evaluation