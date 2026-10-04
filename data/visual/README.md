# Visual Inspection Dataset Directory

> **Asset Target**: `PUMP_001` (Industrial Centrifugal Pump)  
> **Status**: Synthetic Demo Specification & Schema  

---

## Purpose
This directory specifies the visual data assets and inspection catalog used by ForgeGuard AI's computer vision and visual evidence layer.

## Contents
- [`visual_dataset_spec.md`](file:///Users/daakshayani/Desktop/ForgeGuard%20AI/data/visual/visual_dataset_spec.md): Complete catalog of visual defect categories, camera observations, severity tiers, and correlation with mechanical bearing failure modes.

## Real vs Synthetic Data Status
- **Current Repository State**: No physical optical images are bundled in this repository to prevent bloated Git repositories and arbitrary unverified downloads.
- **Demo Mode**: The vision pipeline (`ai/vision/demo.py`) provides validated, structured visual evidence matching the synthetic `PUMP_001` failure scenario.
- **Future Production Ingestion**: Production camera snapshots, drone inspection frames, or high-speed optical feeds can be placed in this directory (e.g. `data/visual/images/`) and processed by `ai/vision/inference.py` once model weights are deployed.
