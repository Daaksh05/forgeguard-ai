# ForgeGuard AI — Industrial Sensor Telemetry Schema

> **Document Type**: Technical Data Specification (Synthetic / Demonstration)  
> **Target Machine Class**: Industrial Centrifugal Pump & Induction Motor System (`PUMP_001`)  
> **Schema Version**: 1.0.0

---

## 1. Overview

This document specifies the telemetry data schema used by ForgeGuard AI for real-time condition monitoring, anomaly detection, and predictive maintenance.

The schema captures key physical, electrical, and thermal parameters designed to detect electro-mechanical degradation patterns—such as bearing wear, cavitation, and motor overload—before catastrophic failure occurs.

---

## 2. Field Definitions

| Field Name | Data Type | Engineering Unit | Normal Range | Alert Threshold | Critical Threshold |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `timestamp` | String (ISO 8601 UTC) | `YYYY-MM-DDTHH:MM:SSZ` | Continuous | N/A | N/A |
| `machine_id` | String | Identifier | `PUMP_001` | N/A | N/A |
| `temperature` | Float (64-bit) | Degrees Celsius (°C) | 55.0 – 68.0 | > 75.0 | > 88.0 |
| `vibration` | Float (64-bit) | mm/s RMS (Velocity) | 1.2 – 2.8 | > 4.5 | > 7.1 |
| `pressure` | Float (64-bit) | bar (Discharge Gauge) | 4.8 – 5.2 | < 4.4 or > 5.6 | < 4.0 or > 6.0 |
| `rpm` | Float (64-bit) | Revolutions / Minute | 1750.0 – 1790.0 | < 1720.0 | < 1680.0 |
| `current` | Float (64-bit) | Amperes (A RMS) | 26.0 – 29.0 | > 31.5 | > 34.0 |
| `ambient_temp` | Float (64-bit) | Degrees Celsius (°C) | 18.0 – 26.0 | > 35.0 | > 42.0 |
| `acoustic_emission` | Float (64-bit) | Decibels (dB) | 32.0 – 45.0 | > 55.0 | > 70.0 |
| `operating_state` | Categorical String | Enum | `RUNNING` | `DEGRADED` | `MAINTENANCE` |

---

## 3. Detailed Field Specifications

### 3.1 `timestamp`
- **Description**: Universal coordinated timestamp for time-series alignment across visual, acoustic, and SCADA channels.
- **Format**: `YYYY-MM-DDTHH:MM:SSZ` (e.g., `2026-10-04T08:00:00Z`)
- **Sampling Frequency**: Default 1-minute to 5-minute intervals.

### 3.2 `machine_id`
- **Description**: Unique asset identifier within the plant registry.
- **Example**: `PUMP_001`

### 3.3 `temperature` (Bearing Housing Temperature)
- **Description**: Contact RTD temperature sensor mounted directly on the drive-end (DE) bearing housing.
- **Normal Meaning**: Thermal equilibrium under continuous rated load (55°C – 68°C).
- **Abnormal Indication**: Rapid increase (>75°C) indicates lubricant breakdown, increased rolling friction, excessive preload, or subsurface race fatigue.

### 3.4 `vibration` (Overall Vibration Velocity RMS)
- **Description**: Tri-axial accelerometer reading filtered to overall RMS velocity (10 Hz – 1000 Hz) per ISO 10816-3 Class II machinery.
- **Normal Meaning**: Smooth rotational baseline (1.2 – 2.8 mm/s).
- **Abnormal Indication**: Increases to 4.5–7.1 mm/s indicate mechanical unbalance, loose footing, or early bearing defect; values >7.1 mm/s indicate severe spalling or imminent cage failure.

### 3.5 `pressure` (Discharge Line Pressure)
- **Description**: Piezoresistive pressure transmitter monitoring fluid output.
- **Normal Meaning**: Stable hydraulic head pressure (4.8 – 5.2 bar).
- **Abnormal Indication**: Pulsations or drops indicate cavitation, impeller blockage, or flow throttling. In pure bearing failure, pressure remains relatively stable until mechanical binding slows the impeller.

### 3.6 `rpm` (Shaft Rotational Speed)
- **Description**: Optical / magnetic tachometer on the driven shaft.
- **Normal Meaning**: Nominal asynchronous motor shaft speed under 50/60 Hz grid supply (1750 – 1790 RPM).
- **Abnormal Indication**: Sudden dips indicate high mechanical resistance / binding.

### 3.7 `current` (Motor Phase Current Draw)
- **Description**: Current transducer measuring RMS phase current drawn by the 30kW drive motor.
- **Normal Meaning**: Steady electrical power consumption under nominal load (26.0 – 29.0 A).
- **Abnormal Indication**: Elevated current (>31.5 A) with constant RPM indicates mechanical drag/friction caused by damaged bearing elements.

### 3.8 `ambient_temp` (Ambient Environment Temperature)
- **Description**: Baseline ambient plant temperature sensor.
- **Normal Meaning**: Environmental climate conditions (18.0 – 26.0 °C).
- **Correlation Purpose**: Allows the AI agent to distinguish between seasonal heat waves and true internal component overheating (differential $\Delta T = T_{bearing} - T_{ambient}$).

### 3.9 `acoustic_emission` (High-Frequency Acoustic Energy)
- **Description**: Ultrasonic acoustic emission sensor (20 kHz – 100 kHz) measuring high-frequency friction stress waves.
- **Normal Meaning**: Quiet baseline lubrication film (32.0 – 45.0 dB).
- **Abnormal Indication**: Jumps early to 55–75 dB as micro-cracks and lubricant breakdown develop, often days before bulk vibration rises.

### 3.10 `operating_state`
- **Description**: Discrete state label of the equipment.
- **Allowed Values**:
  - `RUNNING`: Nominal active production.
  - `STARTUP`: Transient motor ramp-up.
  - `SHUTDOWN`: Controlled ramp-down.
  - `STANDBY`: Powered on but idle.
  - `DEGRADED`: Operating under detected abnormal condition.
  - `MAINTENANCE`: Machine isolated for repair/inspection.

---

## 4. Extensibility & Future Machines

This schema is designed to extend cleanly to other industrial asset classes (e.g., CNC spindles, air compressors, industrial blowers) by adding machine-specific telemetry (e.g., suction pressure, oil particulate count, winding temperature) while maintaining core standardized timestamp, identifier, and state fields.
