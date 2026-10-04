#!/usr/bin/env python3
"""
Synthetic Telemetry Generator for PUMP_001
Generates 100 chronologically ordered, multi-sensor correlated rows
demonstrating normal, incipient degradation, and severe bearing fault stages.
"""

import csv
import math
import random
from datetime import datetime, timedelta

def generate_telemetry():
    random.seed(42)  # Deterministic seed for reproducible evaluation
    start_time = datetime(2026, 10, 4, 8, 0, 0)
    rows = []
    
    total_steps = 100
    for i in range(total_steps):
        t = start_time + timedelta(minutes=5 * i)
        timestamp_str = t.strftime("%Y-%m-%dT%H:%M:%SZ")
        machine_id = "PUMP_001"
        
        # Stage 1: Normal Operation (Steps 0 - 39)
        if i < 40:
            temp = 60.5 + 1.2 * math.sin(i * 0.3) + random.uniform(-0.3, 0.3)
            vib = 1.8 + 0.2 * math.cos(i * 0.4) + random.uniform(-0.1, 0.1)
            press = 5.02 + random.uniform(-0.04, 0.04)
            rpm = 1770.0 + random.uniform(-2.0, 2.0)
            curr = 27.4 + random.uniform(-0.3, 0.3)
            amb = 21.2 + 0.03 * i + random.uniform(-0.2, 0.2)
            ae = 38.0 + random.uniform(-1.5, 1.5)
            state = "RUNNING"
            
        # Stage 2: Incipient Lubricant Degradation & Micro-Wear (Steps 40 - 74)
        elif i < 75:
            progress = (i - 40) / 35.0  # 0.0 to 1.0
            temp = 62.0 + progress * 15.5 + random.uniform(-0.4, 0.4)
            vib = 2.0 + progress * 2.8 + random.uniform(-0.15, 0.2)
            press = 5.01 - progress * 0.08 + random.uniform(-0.04, 0.04)
            rpm = 1769.0 - progress * 4.0 + random.uniform(-2.0, 2.0)
            curr = 27.5 + progress * 4.2 + random.uniform(-0.3, 0.4)
            amb = 22.4 + 0.02 * (i - 40) + random.uniform(-0.2, 0.2)
            ae = 40.0 + progress * 28.0 + random.uniform(-2.0, 2.0)
            state = "RUNNING" if progress < 0.65 else "DEGRADED"
            
        # Stage 3: Severe Bearing Spalling & Thermal/Vibrational Escalation (Steps 75 - 99)
        else:
            progress = (i - 75) / 24.0  # 0.0 to 1.0
            temp = 78.5 + progress * 17.5 + random.uniform(-0.6, 0.6)
            vib = 5.0 + progress * 4.5 + random.uniform(-0.3, 0.4)
            press = 4.90 - progress * 0.22 + random.uniform(-0.06, 0.06)
            rpm = 1764.0 - progress * 10.0 + random.uniform(-3.0, 2.0)
            curr = 31.8 + progress * 4.5 + random.uniform(-0.4, 0.5)
            amb = 23.1 + random.uniform(-0.3, 0.3)
            ae = 69.0 + progress * 16.0 + random.uniform(-2.5, 2.5)
            state = "DEGRADED"

        rows.append({
            "timestamp": timestamp_str,
            "machine_id": machine_id,
            "temperature": round(temp, 2),
            "vibration": round(vib, 2),
            "pressure": round(press, 2),
            "rpm": round(rpm, 1),
            "current": round(curr, 2),
            "ambient_temp": round(amb, 2),
            "acoustic_emission": round(ae, 1),
            "operating_state": state
        })
        
    with open("data/sensors/pump_001_telemetry.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "machine_id", "temperature", "vibration",
            "pressure", "rpm", "current", "ambient_temp",
            "acoustic_emission", "operating_state"
        ])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} telemetry rows in data/sensors/pump_001_telemetry.csv")

if __name__ == "__main__":
    generate_telemetry()
