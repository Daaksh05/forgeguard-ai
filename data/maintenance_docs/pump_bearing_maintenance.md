# Standard Operating Procedure: Centrifugal Pump Bearing Maintenance & Inspection

> **Document ID**: `SOP-MNT-PUMP-042`  
> **Notice**: **DEMONSTRATION / SYNTHETIC MAINTENANCE DOCUMENTATION** (For ForgeGuard AI Evaluation)  
> **Target Equipment**: Industrial Centrifugal Booster Pumps (Series PUMP-30KW / Model `PUMP_001`)  
> **Revision**: 2.4 | **Effective Date**: 2026-01-15

---

## 1. Safety Warnings & Isolation (LOTO)

> [!CAUTION]
> **ELECTRICAL & HIGH TEMPERATURE HAZARD**  
> 1. Always perform **Lockout/Tagout (LOTO)** on the 400V 3-phase motor breaker before opening terminal boxes, coupling guards, or bearing housings.  
> 2. Bearing housings operating above 70°C present severe burn risks. Allow the housing to cool below 45°C or wear heat-resistant PPE before physical contact.  
> 3. Ensure the hydraulic discharge and suction lines are isolated and depressurized before unbolting flange connections.

---

## 2. Maintenance Intervals & Schedule

| Frequency | Service Type | Mandatory Tasks |
| :--- | :--- | :--- |
| **Daily (Shift Walk)** | Visual & Audio Check | Inspect seal leakage, listen for grinding/whining, check housing thermometer gauge. |
| **Weekly (150 Hours)** | Condition Telemetry | Log vibration RMS, acoustic emission dB, and motor current draw. |
| **Monthly (500 Hours)** | Lubrication Service | Inspect grease purge port, purge old grease, re-lubricate with 25g NLGI Grade 2 Polyurea grease. |
| **Annual (4,000 Hours)** | Major Overhaul | Bearing removal, raceway wear analysis, shaft runout inspection, dynamic laser alignment. |

---

## 3. Bearing Degradation Symptoms & Diagnostics

### 3.1 Primary Symptoms
- **High-Frequency Whining / Rumbling**: Indicates micro-pitting or raceway spalling.
- **Progressive Heat Buildup**: Housing temperature exceeding nominal threshold (>70°C).
- **Vibration Amplitude Rise**: Spike in 1X / 2X shaft rotational frequency harmonics and bearing ball pass frequencies (BPFI/BPFO).
- **Grease Expulsion / Discoloration**: Dark, burnt, or metal-flecked grease around bearing labyrinth seals.

### 3.2 Diagnostic Thresholds (ISO 10816-3 Class II Machines)

```
Vibration Velocity (RMS mm/s)
[0.0 ---------------- 2.8]  Zone A/B: Good / Acceptable (Normal continuous operation)
[2.8 ---------------- 4.5]  Zone C: Warning (Lubrication degradation / plan inspection)
[4.5 ---------------- 7.1]  Zone C+: Alert (Schedule immediate planned downtime)
[> 7.1                   ]  Zone D: CRITICAL (Imminent seizure danger — Immediate Shutdown)
```

### 3.3 Temperature Evaluation Rules
- **Normal Operating Range**: $55^\circ\text{C} - 68^\circ\text{C}$
- **Warning Threshold**: $>75^\circ\text{C}$ (or differential $\Delta T > 45^\circ\text{C}$ above ambient)
- **Emergency Shutdown**: $>90^\circ\text{C}$

---

## 4. Inspection & Maintenance Procedures

### 4.1 Step-by-Step Bearing Inspection
1. **Auditory & Ultrasonic Check**:
   - Apply ultrasonic contact probe to the top of the drive-end bearing housing.
   - Normal reading: $<45\text{ dB}$. If $>60\text{ dB}$ with rhythmic popping, inner ring defect is present.
2. **Thermal Imaging & Contact Probe**:
   - Measure temperature at 3 points: Drive-end housing, Non-drive-end housing, and Motor frame.
   - Temperature gradient between DE and NDE bearing should not exceed $12^\circ\text{C}$.
3. **Lubrication Film & Seal Inspection**:
   - Inspect outer labyrinth seals for grease leakage, weeping, or black residue.
   - Clean the grease relief valve and inspect purged lubricant for metallic particles using a magnetic wand.
4. **Coupling & Shaft Runout**:
   - Remove coupling guard and check flexible elastomeric spider insert for shredding or angular misalignment ($<0.05\text{ mm}$ permissible).

### 4.2 Re-lubrication Protocol
- Use only approved **Synthetic Polyurea High-Speed Grease (NLGI Grade 2)**.
- Do not mix lithium-complex grease with polyurea grease (incompatible thickeners will liquefy and flush out).
- Grease quantity: $Q = 0.005 \times D \times B$ grams, where $D$ is outer diameter (mm) and $B$ is bearing width (mm). For standard 6312 bearing: $\approx 25\text{ grams}$.

### 4.3 Corrective Action Matrix

| Observed Condition | Probable Root Cause | Corrective Action |
| :--- | :--- | :--- |
| Elevated Temp (>75°C), Normal Vibration (<2.8 mm/s) | Over-greasing or minor lubricant starvation | Clean relief plug; check grease level. Do not over-pack. |
| Elevated Vibration (>5.0 mm/s), High AE (>65 dB), Temp (>80°C) | Bearing raceway spalling / cage fatigue | Initiate controlled shutdown; replace bearing set (SKF 6312 C3). |
| Sudden Temp Surge (>90°C), Current Spike (>34A) | Mechanical binding / imminent bearing seizure | **EMERGENCY STOP**. Lock out equipment immediately. |
| High Vibration (>6.0 mm/s), Normal Temp (<65°C) | Shaft misalignment or impeller unbalance | Inspect coupling alignment; perform dynamic balance test. |

---

## 5. Document Revision History
- **v1.0 (2024-03-10)**: Initial plant release for centrifugal booster pump series.
- **v2.0 (2025-06-20)**: Added ultrasonic acoustic emission diagnostic thresholds.
- **v2.4 (2026-01-15)**: Integrated multimodal sensor telemetry parameters for automated monitoring.
