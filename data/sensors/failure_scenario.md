# ForgeGuard AI — Industrial Failure Scenario Specification

> **Scenario ID**: `SCENARIO-PUMP001-BEARING-01`  
> **Dataset**: `data/sensors/pump_001_telemetry.csv`  
> **Target Machine**: Centrifugal Slurry Pump `PUMP_001` (Drive-End Bearing)  
> **Primary Failure Mode**: Subsurface Spalling & Inner Raceway Fatigue Initiated by Lubrication Breakdown

---

## 1. Machine Asset Profile

- **Asset ID**: `PUMP_001`
- **Asset Description**: High-pressure centrifugal booster pump driven by a 30 kW 3-phase induction motor.
- **Critical Components**:
  - Drive-End (DE) Deep Groove Ball Bearing (SKF 6312 or equivalent)
  - Mechanical Shaft Seal
  - Cast-iron Bearing Housing with thermal probe and tri-axial accelerometer
  - Flexible Jaw Coupling

---

## 2. Failure Mode & Root Cause

### Root Cause
Progressive lubricant starvation and thermal breakdown in the drive-end bearing cavity leading to metal-to-metal boundary friction, micro-spalling of the inner raceway, and severe vibrational and thermal escalation.

### Progression Timeline
1. **Baseline Phase (Timestamps: 08:00 – 11:15 UTC, Rows 1–40)**:
   - Stable continuous production.
   - Healthy hydrodynamic lubrication film.
   - Vibration velocity nominal at $1.6 - 2.2\text{ mm/s RMS}$ (ISO 10816 Class II "Good" Zone A).
   - Bearing temperature steady at $59.0 - 63.5^\circ\text{C}$ (differential $\Delta T \approx 40^\circ\text{C}$ above ambient).
   - Acoustic emission steady at $36 - 42\text{ dB}$.

2. **Incipient Degradation Phase (Timestamps: 11:20 – 14:10 UTC, Rows 41–75)**:
   - Grease oxidation and oil weeping degrade the fluid film.
   - **Early Symptom 1**: Acoustic emission rises rapidly from $40\text{ dB}$ to $68\text{ dB}$ (ultrasonic friction stress waves).
   - **Early Symptom 2**: Bearing housing temperature steadily climbs from $63^\circ\text{C}$ to $78^\circ\text{C}$ ($\Delta T$ increases while ambient temperature remains flat at $22 - 24^\circ\text{C}$).
   - **Mid Symptom**: Vibration velocity creeps upward from $2.2\text{ mm/s}$ to $4.8\text{ mm/s}$ (entering ISO Warning Zone C).
   - Motor current increases modestly from $27.5\text{ A}$ to $31.4\text{ A}$ due to mechanical resistance.
   - Discharge pressure remains steady at $\sim 5.0\text{ bar}$, confirming no hydraulic cavitation.

3. **Severe Defect / Imminent Failure Phase (Timestamps: 14:15 – 16:15 UTC, Rows 76–100)**:
   - Inner raceway spalling and rolling element surface pitting.
   - Vibration velocity spikes to $5.5 - 9.4\text{ mm/s RMS}$ (violating ISO Critical Threshold $>7.1\text{ mm/s}$, Zone D).
   - Bearing temperature surges toward $96^\circ\text{C}$ with imminent thermal runaway and seizure danger.
   - Acoustic emission surges to $85\text{ dB}$.
   - Motor current reaches $36.1\text{ A}$.
   - Operating state shifts to `DEGRADED`.

---

## 3. Affected Sensors & Anomaly Signature

| Sensor | Baseline Normal | Incipient Degradation | Critical Defect | Anomaly Signature |
| :--- | :--- | :--- | :--- | :--- |
| `acoustic_emission` | 36 – 42 dB | 45 – 68 dB | 70 – 85 dB | **Earliest indicator**; exponential rise in stress waves |
| `temperature` | 59 – 63.5 °C | 64 – 78 °C | 80 – 96.2 °C | Linear thermal rise; uncoupled from ambient temp |
| `vibration` | 1.6 – 2.2 mm/s | 2.5 – 4.8 mm/s | 5.5 – 9.4 mm/s | Exceeds ISO 10816 Class II threshold (>7.1 mm/s) |
| `current` | 27.1 – 27.9 A | 28.2 – 31.4 A | 32.5 – 36.1 A | Increased electrical load due to mechanical friction |
| `pressure` | 4.98 – 5.08 bar | 4.92 – 5.02 bar | 4.70 – 4.88 bar | Relatively stable; minor drop only under severe drag |
| `rpm` | 1768 – 1774 RPM | 1765 – 1770 RPM | 1752 – 1762 RPM | Slight slip increase due to motor torque demand |

---

## 4. Expected ForgeGuard AI Multimodal Detection

When all AI modules are operational, ForgeGuard AI will synthesize evidence across modalities:

```
[Telemetry Anomaly Stream] --------+
 (Vibration + Temp + AE spike)     |
                                   v
[Visual Evidence Feed] ----------> [Multimodal Agent] -----> [Alert & Operator Action Plan]
 (Grease leak / Blistered paint)   |  (Correlates with RAG
                                   |   Maintenance Docs)
[Maintenance Manual RAG] ----------+
 (ISO 10816 / Relubrication SOP)
```

### Expected ForgeGuard Alert:
- **Alert Level**: `CRITICAL — IMMEDIATE ACTION REQUIRED`
- **Machine ID**: `PUMP_001` (Component: Drive-End Bearing Assembly)
- **Anomaly Classification**: Bearing Raceway Degradation / Severe Lubricant Failure
- **Confidence Score**: 96.4%
- **Evidence Corroboration**:
  1. *Sensor*: Multi-sensor cross-correlation detected (Vibration 9.4 mm/s + Temp 96.2°C + AE 85 dB).
  2. *Visual*: Corroborates with grease seal weeping and housing paint thermal discoloration (see `visual_evidence_spec.md`).
  3. *Domain Knowledge*: Matches Failure Mode B-03 in `pump_bearing_maintenance.md`.

---

## 5. Recommended Operator Action

1. **Immediate Action**:
   - Issue controlled shutdown of `PUMP_001` within 30 minutes to prevent catastrophic shaft seizure or stator motor damage.
   - Switch plant load to auxiliary standby pump `PUMP_002`.
2. **Lockout / Tagout (LOTO)**:
   - Isolate 400V electrical power feed and depressurize discharge line.
3. **Physical Inspection**:
   - Inspect drive-end bearing housing for lubricant leakage, seal damage, and thermal discoloration.
   - Check radial and axial shaft runout.
4. **Maintenance Task**:
   - Disassemble bearing housing and replace bearing assembly (SKF 6312 C3).
   - Flush and replenish with high-temperature synthetic polyurea grease.
   - Perform laser shaft alignment prior to restarting.
