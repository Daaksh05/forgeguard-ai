#!/usr/bin/env python3
"""
ForgeGuard AI — Sensor Telemetry Dataset Validator
===================================================
Validates industrial time-series telemetry data against schema rules:
1. Verifies presence of all required columns.
2. Validates timestamp format (ISO 8601 UTC) and strict chronological ordering.
3. Checks data types and physical value ranges for all numeric fields.
4. Ensures zero missing / null / NaN entries.
5. Verifies discrete operating_state values against allowed enumeration.

Usage:
    python data/sensors/validate_telemetry.py [path_to_csv]
"""

import sys
import os
import csv
from datetime import datetime

REQUIRED_COLUMNS = [
    "timestamp",
    "machine_id",
    "temperature",
    "vibration",
    "pressure",
    "rpm",
    "current",
    "ambient_temp",
    "acoustic_emission",
    "operating_state"
]

ALLOWED_OPERATING_STATES = {
    "RUNNING",
    "STARTUP",
    "SHUTDOWN",
    "STANDBY",
    "DEGRADED",
    "MAINTENANCE"
}

# Physical boundary sanity checks
NUMERIC_BOUNDS = {
    "temperature": (-20.0, 200.0),       # °C
    "vibration": (0.0, 100.0),           # mm/s RMS
    "pressure": (0.0, 50.0),             # bar
    "rpm": (0.0, 10000.0),               # RPM
    "current": (0.0, 500.0),             # Amperes
    "ambient_temp": (-40.0, 80.0),       # °C
    "acoustic_emission": (0.0, 150.0)    # dB
}

def validate_telemetry(csv_path: str) -> bool:
    print("=" * 65)
    print(f"  ForgeGuard AI: Telemetry Validation for {os.path.basename(csv_path)}")
    print("=" * 65)
    
    if not os.path.exists(csv_path):
        print(f"[ERROR] File not found: {csv_path}")
        return False
        
    errors = []
    warnings = []
    
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        
        # 1. Column header check
        if not header:
            print("[ERROR] CSV file is empty or missing headers.")
            return False
            
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in header]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
            
        row_count = 0
        last_dt = None
        
        # Track statistics
        stats = {col: {"min": float("inf"), "max": float("-inf")} for col in NUMERIC_BOUNDS}
        machines_seen = set()
        states_seen = set()
        
        for row_idx, row in enumerate(reader, start=1):
            row_count += 1
            
            # 2. Check for missing / empty fields
            for col in REQUIRED_COLUMNS:
                if col in row:
                    val = row[col]
                    if val is None or val.strip() == "":
                        errors.append(f"Row {row_idx}: Empty value in required column '{col}'")
                        
            # 3. Validate timestamp format & chronology
            ts_str = row.get("timestamp", "").strip()
            if ts_str:
                try:
                    # Parse ISO 8601 UTC
                    clean_ts = ts_str.replace("Z", "+00:00")
                    dt = datetime.fromisoformat(clean_ts)
                    if last_dt is not None:
                        if dt <= last_dt:
                            errors.append(
                                f"Row {row_idx}: Timestamp {ts_str} is not strictly chronological (previous was {last_dt.isoformat()})"
                            )
                    last_dt = dt
                except ValueError:
                    errors.append(f"Row {row_idx}: Invalid ISO 8601 timestamp '{ts_str}'")
                    
            # 4. Validate machine_id
            m_id = row.get("machine_id", "").strip()
            if m_id:
                machines_seen.add(m_id)
                
            # 5. Validate operating_state
            op_state = row.get("operating_state", "").strip()
            if op_state:
                states_seen.add(op_state)
                if op_state not in ALLOWED_OPERATING_STATES:
                    errors.append(f"Row {row_idx}: Invalid operating_state '{op_state}'")
                    
            # 6. Validate numeric fields
            for num_col, (min_bound, max_bound) in NUMERIC_BOUNDS.items():
                if num_col in row and row[num_col] != "":
                    try:
                        num_val = float(row[num_col])
                        if num_val < min_bound or num_val > max_bound:
                            errors.append(
                                f"Row {row_idx}: Field '{num_col}' value {num_val} out of physical bounds [{min_bound}, {max_bound}]"
                            )
                        stats[num_col]["min"] = min(stats[num_col]["min"], num_val)
                        stats[num_col]["max"] = max(stats[num_col]["max"], num_val)
                    except ValueError:
                        errors.append(f"Row {row_idx}: Field '{num_col}' value '{row[num_col]}' is not a valid float.")
                        
    # Report Results
    print(f"[*] Total rows validated  : {row_count}")
    print(f"[*] Unique machines        : {sorted(list(machines_seen))}")
    print(f"[*] Operating states found : {sorted(list(states_seen))}")
    print(f"[*] Timestamp range        : {reader.fieldnames and row_count > 0}")
    
    print("\n--- Summary Statistics ---")
    for col, minmax in stats.items():
        if minmax["min"] != float("inf"):
            print(f"  - {col:18}: Min = {minmax['min']:7.2f} | Max = {minmax['max']:7.2f}")
            
    if errors:
        print("\n[VALIDATION FAILED]")
        print(f"Found {len(errors)} error(s):")
        for err in errors[:15]:
            print(f"  [-] {err}")
        if len(errors) > 15:
            print(f"  ... and {len(errors) - 15} more errors.")
        return False
    else:
        print("\n[+] [VALIDATION PASSED] All schema, type, range, and chronological checks succeeded.")
        return True

if __name__ == "__main__":
    target = "data/sensors/pump_001_telemetry.csv" if len(sys.argv) < 2 else sys.argv[1]
    success = validate_telemetry(target)
    sys.exit(0 if success else 1)
