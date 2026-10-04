# ForgeGuard AI — Visual Dataset Specification (Synthetic / Demonstration)

> **Document Target**: `data/visual/`  
> **Target Machine**: Industrial Centrifugal Pump System (`PUMP_001`)  
> **Status**: Specification & Synthetic Demo Catalog (No Physical Images Ingested)

---

## 1. Overview & Dataset Context

This specification defines the visual condition catalog and inspection criteria for ForgeGuard AI's computer vision layer.

In industrial plant environments, fixed optical cameras and automated inspection payloads capture high-resolution imagery of critical asset components (drive-end bearing housing, labyrinth shaft seals, flexible jaw couplings, and baseplate foundations).

> **Synthetic / Demo Disclaimer**: Real industrial camera feeds are not yet ingested in this repository. All visual defect definitions and demonstration evidence below are synthetic references calibrated to the PUMP_001 bearing degradation failure scenario.

---

## 2. Visual Defect Categories

The vision pipeline monitors six discrete visual condition categories aligned with mechanical bearing failure modes:

| Defect ID | Category Name | Severity | Primary Target Component |
| :--- | :--- | :--- | :--- |
| `NORMAL_OPERATION` | Normal Machine Exterior | `NORMAL` | Full Pump Assembly |
| `DEFECT_OIL_LEAK` | Oil / Grease Seal Leakage | `MEDIUM` – `HIGH` | Drive-End Labyrinth Seal & Baseplate |
| `DEFECT_THERMAL_DISCOLOR` | Thermal Paint Blistering | `HIGH` – `CRITICAL` | Cast-Iron Bearing Housing Hub |
| `DEFECT_HOUSING_CRACK` | Structural Fatigue Cracks | `CRITICAL` | Bearing Pillow Block & Footings |
| `DEFECT_SEAL_CONTAMINATION` | Seal Degradation & Ingress | `MEDIUM` | Elastomeric Lip Seal & Shaft Entry |
| `DEFECT_COUPLING_WEAR` | Flexible Coupling Shredding | `HIGH` | Motor-to-Pump Coupling Hub |

---

## 3. Detailed Category Specifications

### 3.1 Normal Machine Exterior (`NORMAL_OPERATION`)
- **Camera Observation**:
  - Clean, intact epoxy enamel paint across the bearing housing and motor frame.
  - Dry shaft seal interfaces with zero fluid weeping or droplet accumulation.
  - Symmetrical flexible coupling alignment with no elastomeric debris on baseplate.
- **Severity**: `NORMAL`
- **Relationship to Bearing Degradation**:
  - Corresponds to healthy baseline operation ($08:00 - 11:15\text{ UTC}$).
- **Expected Evidence Description**:
  - *Observation*: "Intact surface coating; shaft seal boundary is dry and free of lubricant egress; coupling hub aligned with zero particulate debris."
  - *Interpretation*: "Normal nominal machine state; no visual indications of thermal or mechanical distress."

---

### 3.2 Oil / Grease Seal Leakage (`DEFECT_OIL_LEAK`)
- **Camera Observation**:
  - Dark, viscous fluid weeping or droplet trails emerging from the labyrinth shaft seal or bearing end cap.
  - Wet grime pool accumulation on the baseplate beneath the drive-end bearing.
- **Severity**: `MEDIUM` (early weeping) to `HIGH` (heavy fluid leakage)
- **Relationship to Bearing Degradation**:
  - Primary root cause and early indicator of lubricant starvation. Seal weeping allows grease loss while enabling abrasive slurry particulate ingress into the bearing raceway.
- **Expected Evidence Description**:
  - *Observation*: "Dark viscous fluid film and droplets observed radiating from the drive-end labyrinth seal onto the baseplate (bounding region: $[x: 0.42, y: 0.55, w: 0.18, h: 0.22]$)."
  - *Interpretation*: "Active lubricant seal breach indicating lubricant depletion and risk of metal-to-metal raceway friction."

---

### 3.3 Thermal Paint Blistering & Discoloration (`DEFECT_THERMAL_DISCOLOR`)
- **Camera Observation**:
  - Severe thermal discoloration (yellowing, browning, or charring) of industrial enamel paint on the cast-iron bearing housing.
  - Localized paint bubbling, flaking, or thermal haze around the bearing hub.
- **Severity**: `HIGH` to `CRITICAL`
- **Relationship to Bearing Degradation**:
  - Direct visual proof of prolonged bearing housing surface temperatures exceeding $85^\circ\text{C} - 100^\circ\text{C}$, confirming intense internal friction and imminent cage seizure.
- **Expected Evidence Description**:
  - *Observation*: "Localized paint bubbling, charring, and severe dark thermal discoloration centered around the drive-end bearing hub (bounding region: $[x: 0.38, y: 0.32, w: 0.25, h: 0.28]$)."
  - *Interpretation*: "Severe internal frictional overheating in bearing cavity; corroborates sensor telemetry thermal runaway."

---

### 3.4 Bearing Housing Structural Damage / Cracks (`DEFECT_HOUSING_CRACK`)
- **Camera Observation**:
  - Fine surface fissures, fractures, or crack propagation across the cast-iron bearing pillow block or mounting pedestal.
  - Backed-out or loose mounting bolts on the pedestal base.
- **Severity**: `CRITICAL`
- **Relationship to Bearing Degradation**:
  - Result of extreme cyclic mechanical fatigue and excessive vibration amplitude ($>7.1\text{ mm/s RMS}$, ISO Zone D) shaking the assembly.
- **Expected Evidence Description**:
  - *Observation*: "Linear surface fissure propagating across the upper cast-iron bearing housing pillow block."
  - *Interpretation*: "Structural fatigue cracking resulting from severe continuous mechanical vibration and dynamic unbalance."

---

### 3.5 Seal Degradation & Environmental Contamination (`DEFECT_SEAL_CONTAMINATION`)
- **Camera Observation**:
  - Torn, frayed, or degraded elastomeric lip seal protruding from the shaft entry.
  - Excessive dry dust, sludge, or abrasive mineral slurry buildup caked around the bearing entrance.
- **Severity**: `MEDIUM`
- **Relationship to Bearing Degradation**:
  - External particulates act as an abrasive grinding compound inside the bearing cavity, initiating raceway micro-spalling and pitting.
- **Expected Evidence Description**:
  - *Observation*: "Degraded, torn elastomeric lip seal with abrasive particulate slurry accumulation around shaft collar."
  - *Interpretation*: "Environmental seal barrier compromised; high probability of particulate contamination inside bearing raceway."

---

### 3.6 Flexible Coupling Misalignment & Shredding (`DEFECT_COUPLING_WEAR`)
- **Camera Observation**:
  - Black rubber/polyurethane shavings and elastomer dust on the pump baseplate beneath the coupling guard.
  - Visible angular or parallel gap offset between motor and pump coupling hubs.
- **Severity**: `HIGH`
- **Relationship to Bearing Degradation**:
  - Severe shaft misalignment imparts heavy cyclic radial and axial shock loads directly onto the drive-end bearing, reducing bearing L10h fatigue life by up to 80%.
- **Expected Evidence Description**:
  - *Observation*: "Polyurethane coupling insert shavings accumulated beneath coupling guard with visible angular offset between shafts."
  - *Interpretation*: "Severe shaft coupling misalignment imparting abnormal radial fatigue loads on drive-end bearing."

---

## 4. Multimodal Correlation Reference

| Visual Defect | Severity | Corroborating Telemetry Signature | Maintenance Doc Reference |
| :--- | :--- | :--- | :--- |
| `DEFECT_OIL_LEAK` | `MEDIUM`/`HIGH` | Acoustic Emission $\uparrow$ ($>50\text{ dB}$), Temp $\uparrow$ ($>68^\circ\text{C}$) | `pump_bearing_maintenance.md` §4.1 |
| `DEFECT_THERMAL_DISCOLOR` | `HIGH`/`CRITICAL` | Temp $>85^\circ\text{C}$, Current $>32\text{ A}$, $\Delta T > 45^\circ\text{C}$ | `pump_bearing_maintenance.md` §3.3 |
| `DEFECT_HOUSING_CRACK` | `CRITICAL` | Vibration $>7.1\text{ mm/s RMS}$ (ISO Zone D) | `pump_bearing_maintenance.md` §3.2 |
| `DEFECT_SEAL_CONTAMINATION` | `MEDIUM` | Acoustic Emission $>55\text{ dB}$ | `pump_bearing_maintenance.md` §4.2 |
| `DEFECT_COUPLING_WEAR` | `HIGH` | Vibration $\uparrow$ (1X/2X harmonics), Current $\uparrow$ | `pump_bearing_maintenance.md` §4.1 |
