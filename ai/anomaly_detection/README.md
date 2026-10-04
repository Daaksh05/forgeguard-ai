# Sensor Telemetry Anomaly Detection Engine (Phase 4)

> **Module**: `ai/anomaly_detection`  
> **Status**: Operational  
> **Approach**: Hybrid Deterministic Physics Limits + Rolling Statistical Z-Scores + Multi-Sensor Correlation (Zero Black-Box ML)

---

## 1. Overview

The **Sensor Telemetry Anomaly Detection Engine** transforms raw, multivariate time-series industrial telemetry into explainable, structured anomaly evidence.

Designed specifically for industrial rotating machinery (e.g. centrifugal pumps, electric motors, compressors), it tracks the progressive degradation of mechanical components—such as drive-end bearing lubrication breakdown, raceway micro-spalling, and thermal runaway.

```
+-------------------------------------------------------------------------------+
|                      Sensor Telemetry Ingestion (CSV)                         |
|     (temperature, vibration, pressure, rpm, current, acoustic, ambient)       |
+---------------------------------------+---------------------------------------+
                                        |
        +-------------------------------+-------------------------------+
        |                                                               |
        v                                                               v
+-------------------------------+                       +-------------------------------+
|    Engineering Limits Layer   |                       |  Statistical Tracking Layer   |
|   (ISO 10816 / Schema Limits) |                       | (Baseline & Rolling Z-Scores) |
+---------------+---------------+                       +---------------+---------------+
                |                                                               |
                +-------------------------------+-------------------------------+
                                                |
                                                v
                               +---------------------------------+
                               |    Per-Sensor Anomaly Scoring   |
                               |    (NORMAL, LOW, MED, HIGH,     |
                               |             CRITICAL)           |
                               +----------------+----------------+
                                                |
                                                v
                               +---------------------------------+
                               | Multi-Sensor Cross-Correlation  |
                               | (Bearing Friction Triad,        |
                               |  Thermal Decoupling ΔT,         |
                               |  Mechanical vs Hydraulic Check) |
                               +----------------+----------------+
                                                |
                                                v
                               +---------------------------------+
                               |  Machine-Level Risk Assessment  |
                               |  (Risk Score 0-100 & Stages:    |
                               |   HEALTHY -> EARLY_DEGRADATION  |
                               |   -> SEVERE_DEGRADATION)        |
                               +----------------+----------------+
                                                |
                                                v
                               +---------------------------------+
                               |   Structured Evidence Output    |
                               |      (JSON Report & Plots)      |
                               +---------------------------------+
```

---

## 2. Detection Methodology

The detection engine combines three complementary analytical layers to maximize early detection while minimizing false alarms:

### A. Engineering Physical Thresholds
Hard engineering and standard ISO operating boundaries define Alert and Critical limits:

| Sensor | Normal Envelope | Alert Threshold | Critical Threshold | Engineering Reference |
| :--- | :--- | :--- | :--- | :--- |
| **`temperature`** | 55.0 – 68.0 °C | > 75.0 °C | > 88.0 °C | Bearing housing thermal probe |
| **`vibration`** | 1.2 – 2.8 mm/s | > 4.5 mm/s | > 7.1 mm/s | ISO 10816-3 Class II (Zone C/D) |
| **`acoustic_emission`**| 32.0 – 45.0 dB | > 55.0 dB | > 70.0 dB | High-frequency stress waves (20–100 kHz) |
| **`current`** | 26.0 – 29.0 A | > 31.5 A | > 34.0 A | 30 kW motor phase current draw |
| **`pressure`** | 4.8 – 5.2 bar | < 4.4 or > 5.6 bar | < 4.0 or > 6.0 bar | Discharge gauge line pressure |
| **`rpm`** | 1750 – 1790 RPM | < 1720 RPM | < 1680 RPM | Shaft rotational speed |
| **`ambient_temp`** | 18.0 – 26.0 °C | > 35.0 °C | > 42.0 °C | Ambient plant climate baseline |

### B. Statistical Baseline & Rolling Z-Scores
To detect incipient degradation **before** static engineering thresholds are breached:
1. **Healthy Baseline Estimation**: Parameters ($\mu_{base}, \sigma_{base}$) are established over the initial operational period.
2. **Standardized Deviation ($Z$-score)**:
   $$Z_t = \frac{x_t - \mu_{base}}{\max(\sigma_{base}, \epsilon)}$$
3. **Statistical Significance Check**: Drifts are flagged when $|Z_t| \ge 3.0\sigma$ and physical deviation exceeds $20\%$ of the sensor's nominal operating span, avoiding false triggers on stationary sensor noise.

### C. Multi-Sensor Cross-Correlation Patterns
Single sensors can produce localized anomalies. Multi-sensor correlation identifies compound failure syndromes:

1. **Bearing Lubrication Breakdown & Friction Triad**:
   - Simultaneous elevation of `acoustic_emission`, `temperature`, `vibration`, and `current`.
   - Captures progression: Ultrasonic stress waves (early micro-friction) $\to$ Thermal climb $\to$ Raceway spalling $\to$ Mechanical drag on motor.
2. **Thermal Decoupling ($\Delta T$)**:
   $$\Delta T = T_{bearing} - T_{ambient}$$
   - When $\Delta T > 45.0^\circ\text{C}$ and ambient temperature is within normal limits, confirms internal heat generation rather than weather-induced environmental heating.
3. **Mechanical vs Hydraulic Isolation**:
   - Elevated vibration and temperature while discharge line pressure remains stable ($4.8 - 5.2\text{ bar}$) rules out pump cavitation or downstream line blockages, confirming an isolated mechanical bearing defect.

---

## 3. Severity Classification & Machine Risk Scoring

### Severity Levels
- **`NORMAL`** (Score: 0 – 15): Within normal engineering band and normal statistical distribution.
- **`LOW`** (Score: 16 – 39): Incipient statistical drift within safe physical envelope.
- **`MEDIUM`** (Score: 40 – 64): Moderate parameter deviation exceeding normal range or high $Z$-score ($>4.5\sigma$).
- **`HIGH`** (Score: 65 – 84): Breach of Alert threshold (e.g., ISO Zone C vibration $>4.5\text{ mm/s}$, Temp $>75^\circ\text{C}$).
- **`CRITICAL`** (Score: 85 – 100): Breach of Critical threshold (e.g., ISO Zone D vibration $>7.1\text{ mm/s}$, Temp $>88^\circ\text{C}$).

### Machine Health Status
- **`HEALTHY`**: No active alerts; baseline continuous operation.
- **`EARLY_DEGRADATION`**: Initial parameter elevation (e.g. acoustic emission rising, early thermal climb).
- **`SEVERE_DEGRADATION`**: Multiple correlated alerts or critical threshold breaches requiring maintenance intervention.

---

## 4. Structured Evidence Format

### Individual Sensor Anomaly Object
```json
{
  "machine_id": "PUMP_001",
  "timestamp": "2026-10-04T16:15:00Z",
  "sensor": "vibration",
  "observed_value": 9.75,
  "baseline_value": 1.77,
  "threshold": 7.1,
  "anomaly_score": 100.0,
  "severity": "CRITICAL",
  "evidence": "Observed vibration of 9.75 mm/s RMS breached CRITICAL threshold (7.1 mm/s RMS) with statistical deviation Z=+50.04σ (baseline: 1.77 mm/s RMS).",
  "possible_implication": "Mechanical unbalance, misalignment, or raceway spalling (ISO 10816-3 Zone C/D)."
}
```

### Machine-Level Summary Object
```json
{
  "machine_id": "PUMP_001",
  "timestamp": "2026-10-04T16:15:00Z",
  "health_status": "SEVERE_DEGRADATION",
  "risk_score": 100.0,
  "severity": "CRITICAL",
  "anomalous_sensors": [
    "temperature",
    "vibration",
    "pressure",
    "rpm",
    "current",
    "acoustic_emission"
  ],
  "correlated_evidence": [
    {
      "machine_id": "PUMP_001",
      "timestamp": "2026-10-04T16:15:00Z",
      "pattern_name": "BEARING_LUBRICATION_DEGRADATION",
      "involved_sensors": ["acoustic_emission", "temperature", "vibration", "current"],
      "correlation_score": 100.0,
      "severity": "CRITICAL",
      "description": "Multi-sensor triad detected across acoustic_emission, temperature, vibration, current: Acoustic stress waves (85.2 dB), thermal escalation (96.5 °C), and elevated vibration velocity (9.75 mm/s) indicate active bearing degradation.",
      "root_cause_hypothesis": "Progressive boundary lubrication breakdown causing inner raceway micro-spalling, rotational friction, and rapid component wear."
    }
  ],
  "summary": "Severe electro-mechanical degradation active on PUMP_001. Multiple critical telemetry violations detected across temperature, vibration, pressure, rpm, current, acoustic_emission. High risk of imminent bearing seizure or mechanical breakdown."
}
```

---

## 5. Usage Commands

### 1. Run Unit Tests
```bash
python3 -m unittest discover -s ai/anomaly_detection/tests -v
```

### 2. Run Telemetry Anomaly Detection CLI
```bash
# Print summary to terminal
python3 ai/anomaly_detection/run_detection.py \
  --input data/sensors/pump_001_telemetry.csv

# Export full structured JSON evidence
python3 ai/anomaly_detection/run_detection.py \
  --input data/sensors/pump_001_telemetry.csv \
  --output results/pump_001_anomalies.json
```

### 3. Generate Anomaly Visualization Plot
```bash
python3 ai/anomaly_detection/plot_results.py \
  --input data/sensors/pump_001_telemetry.csv \
  --output results/pump_001_anomaly_plot.png
```

---

## 6. Limitations & Synthetic Data Notice

> **IMPORTANT**: This engine is configured and evaluated on synthetic demonstration telemetry (`pump_001_telemetry.csv`) generated for testing and hackathon demonstration purposes. While engineering limits are derived from real-world ISO 10816 standards and industrial centrifugal pump specifications, empirical statistical thresholds must be calibrated against historical baseline telemetry before real-world production deployment.
