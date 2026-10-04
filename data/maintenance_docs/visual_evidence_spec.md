# ForgeGuard AI — Visual Evidence & Computer Vision Specification

> **Module Target**: `ai/vision/` (Visual Defect & Condition Detection)  
> **Target Machine**: Industrial Centrifugal Pump System (`PUMP_001`)  
> **Document Status**: Synthetic / Demo Specification

---

## 1. Overview

This specification establishes the visual condition catalog for ForgeGuard AI's future computer vision pipeline. Fixed optical cameras and inspection imaging feeds will monitor the pump exterior, bearing housings, seals, and shaft couplings.

The visual evidence extracted by the vision module provides critical physical corroboration for the telemetry anomaly detector and RAG reasoning agent.

---

## 2. Visual Defect Catalog

### 2.1 Oil / Grease Seal Leakage (`DEFECT_OIL_LEAK`)
- **Camera Observation**:
  - Dark, viscous fluid film or droplet trails oozing from the labyrinth shaft seal or bearing end cap.
  - Wet grime accumulation on the pump baseplate beneath the drive-end bearing.
- **Severity Rating**: `MEDIUM` to `HIGH`
- **Relationship to Bearing Degradation**:
  - Direct root cause and early indicator of lubricant starvation. Seal failure allows lubricant to escape and external particulates (dust, slurry) to enter the bearing cavity, accelerating metal-to-metal raceway wear.
- **Telemetry Correlation**:
  - Accompanied by gradual rise in `acoustic_emission` (>50 dB) and subsequent increase in `temperature`.

---

### 2.2 Thermal Paint Blistering & Discoloration (`DEFECT_THERMAL_DISCOLOR`)
- **Camera Observation**:
  - Heat-induced discoloration (yellowing, browning, or charring) of industrial enamel paint on the cast-iron bearing housing.
  - Localized paint bubbling, flaking, or thermal haze around the bearing hub.
- **Severity Rating**: `HIGH` to `CRITICAL`
- **Relationship to Bearing Degradation**:
  - Indicates prolonged surface temperatures exceeding 85°C – 100°C caused by severe internal rolling friction or impending seizure.
- **Telemetry Correlation**:
  - Strong correlation with `temperature` readings >85°C and `current` draw >32 A.

---

### 2.3 Bearing Housing Structural Damage / Cracks (`DEFECT_HOUSING_CRACK`)
- **Camera Observation**:
  - Fine surface fissures, fractures, or crack propagation across the cast-iron bearing pillow block or mounting feet.
  - Loose or backed-out mounting bolts on the pedestal base.
- **Severity Rating**: `CRITICAL`
- **Relationship to Bearing Degradation**:
  - Result of extreme cyclic mechanical fatigue and excessive vibration amplitude (>7.0 mm/s) shaking the assembly.
- **Telemetry Correlation**:
  - Strong correlation with high `vibration` velocity spikes (>7.1 mm/s) and harmonic resonance.

---

### 2.4 Seal Degradation & Environmental Contamination (`DEFECT_SEAL_CONTAMINATION`)
- **Camera Observation**:
  - Torn, frayed, or degraded elastomeric lip seal protruding from the shaft opening.
  - Excessive dust, sludge, or crystalline slurry buildup caked around the bearing entrance.
- **Severity Rating**: `MEDIUM`
- **Relationship to Bearing Degradation**:
  - Contaminants act as an abrasive grinding compound inside the raceway, rapidly causing micro-pitting and 3-body abrasive wear.
- **Telemetry Correlation**:
  - Correlates with elevated high-frequency `acoustic_emission` and early `vibration` increases.

---

### 2.5 Flexible Coupling Misalignment & Shredding (`DEFECT_COUPLING_WEAR`)
- **Camera Observation**:
  - Black rubber/polyurethane shavings, elastomer dust on baseplate, or visible angular gap between motor and pump coupling hubs.
- **Severity Rating**: `HIGH`
- **Relationship to Bearing Degradation**:
  - Misalignment imparts severe radial and axial shock loads directly onto the drive-end bearing, cutting bearing lifespan by over 80%.
- **Telemetry Correlation**:
  - Correlates with elevated 1X/2X `vibration` and slight increase in motor `current`.

---

## 3. Visual Detection Integration Matrix

| Visual Defect ID | Severity | Corroborating Telemetry | RAG Document Reference |
| :--- | :--- | :--- | :--- |
| `DEFECT_OIL_LEAK` | Medium | Acoustic Emission $\uparrow$, Temp $\uparrow$ | `pump_bearing_maintenance.md` §4.1 (Lubrication Check) |
| `DEFECT_THERMAL_DISCOLOR` | Critical | Temp $>85^\circ\text{C}$, Current $\uparrow$ | `pump_bearing_maintenance.md` §3.3 (Thermal Evaluation) |
| `DEFECT_HOUSING_CRACK` | Critical | Vibration $>7.1\text{ mm/s}$ (Zone D) | `pump_bearing_maintenance.md` §3.2 (ISO 10816-3 Thresholds) |
| `DEFECT_SEAL_CONTAMINATION` | Medium | Acoustic Emission $>55\text{ dB}$ | `pump_bearing_maintenance.md` §4.2 (Grease Protocol) |
| `DEFECT_COUPLING_WEAR` | High | Vibration $\uparrow$, Current $\uparrow$ | `pump_bearing_maintenance.md` §4.1 (Coupling Inspection) |

---

## 4. Input Specifications for Vision Models (Future Phase)
- **Image Input Format**: RGB images / video frames (1080p, 30 FPS stream or snapshot triggers).
- **Target Output**: Bounding boxes, defect class labels, and detection confidence scores (0.0 – 1.0).
- **Hardware Target**: AMD Instinct / ROCm accelerated vision transformer (ViT / YOLO-based lightweight detector).
