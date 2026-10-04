# Industrial Sensor Telemetry Data

> **Notice**: **DEMONSTRATION & SYNTHETIC DATASET**  
> All datasets, failure patterns, and telemetry signals in this directory are synthetically generated for benchmark evaluation, AI pipeline development, and demonstration purposes. They do not represent proprietary or confidential data from any live industrial facility.

---

## Purpose
This directory stores time-series sensor telemetry data, data schemas, failure scenario definitions, and data validation tooling for the ForgeGuard AI predictive maintenance pipeline.

---

## Directory Contents

| File | Description | Status |
| :--- | :--- | :--- |
| [`schema.md`](file:///Users/daakshayani/Desktop/ForgeGuard%20AI/data/sensors/schema.md) | Full specification of the 10-field telemetry schema, units, engineering limits, and anomaly meanings. | Complete |
| [`pump_001_telemetry.csv`](file:///Users/daakshayani/Desktop/ForgeGuard%20AI/data/sensors/pump_001_telemetry.csv) | 100-row synthetic time-series dataset capturing normal baseline, gradual lubricant degradation, and severe bearing spalling. | Complete |
| [`failure_scenario.md`](file:///Users/daakshayani/Desktop/ForgeGuard%20AI/data/sensors/failure_scenario.md) | Technical profile of the `PUMP_001` bearing degradation scenario, failure stages, affected sensors, and expected alerts. | Complete |
| [`validate_telemetry.py`](file:///Users/daakshayani/Desktop/ForgeGuard%20AI/data/sensors/validate_telemetry.py) | Lightweight Python script verifying CSV schema compliance, timestamps, ranges, and chronological ordering. | Complete |

---

## Validation
To re-run telemetry schema validation:
```bash
python data/sensors/validate_telemetry.py
```
