"""
ForgeGuard AI — Sensor Anomaly Detection Configuration
Centralized definitions for engineering thresholds, rolling windows,
statistical thresholds, sensor weights, and correlation rules.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class SensorThreshold:
    """Threshold specification for a single sensor channel."""
    name: str
    unit: str
    normal_min: float
    normal_max: float
    alert_min: Optional[float] = None
    alert_max: Optional[float] = None
    critical_min: Optional[float] = None
    critical_max: Optional[float] = None
    implication_high: str = ""
    implication_low: str = ""


# Standard sensor thresholds per schema.md (ISO 10816 / Centrifugal Pump Spec)
SENSOR_THRESHOLDS: Dict[str, SensorThreshold] = {
    "temperature": SensorThreshold(
        name="temperature",
        unit="°C",
        normal_min=55.0,
        normal_max=68.0,
        alert_max=75.0,
        critical_max=88.0,
        implication_high="Elevated bearing friction, lubricant breakdown, or excessive preload.",
        implication_low="Abnormally low temperature or sensor disconnect."
    ),
    "vibration": SensorThreshold(
        name="vibration",
        unit="mm/s RMS",
        normal_min=1.2,
        normal_max=2.8,
        alert_max=4.5,
        critical_max=7.1,
        implication_high="Mechanical unbalance, misalignment, or raceway spalling (ISO 10816-3 Zone C/D).",
        implication_low="Sensor loss of signal or equipment uncoupled."
    ),
    "pressure": SensorThreshold(
        name="pressure",
        unit="bar",
        normal_min=4.8,
        normal_max=5.2,
        alert_min=4.4,
        alert_max=5.6,
        critical_min=4.0,
        critical_max=6.0,
        implication_high="Discharge line overpressure or downstream blockage.",
        implication_low="Cavitation, suction restriction, or seal/impeller leakage."
    ),
    "rpm": SensorThreshold(
        name="rpm",
        unit="RPM",
        normal_min=1750.0,
        normal_max=1790.0,
        alert_min=1720.0,
        critical_min=1680.0,
        implication_high="Overspeed condition.",
        implication_low="Severe mechanical binding, high load drag, or motor slip."
    ),
    "current": SensorThreshold(
        name="current",
        unit="A",
        normal_min=26.0,
        normal_max=29.0,
        alert_max=31.5,
        critical_max=34.0,
        implication_high="Motor overload caused by mechanical friction drag or electrical imbalance.",
        implication_low="Underload, coupling detachment, or phase loss."
    ),
    "ambient_temp": SensorThreshold(
        name="ambient_temp",
        unit="°C",
        normal_min=18.0,
        normal_max=26.0,
        alert_max=35.0,
        critical_max=42.0,
        implication_high="High ambient plant temperature impacting heat dissipation.",
        implication_low="Low ambient plant temperature."
    ),
    "acoustic_emission": SensorThreshold(
        name="acoustic_emission",
        unit="dB",
        normal_min=32.0,
        normal_max=45.0,
        alert_max=55.0,
        critical_max=70.0,
        implication_high="Ultrasonic stress waves from boundary friction, micro-cracks, or grease starvation.",
        implication_low="Acoustic sensor detachment or machine shutdown."
    )
}

# Sensor relative criticality weights for machine-level risk calculation
# Sum of weights equals 1.0 for normalized scoring
SENSOR_WEIGHTS: Dict[str, float] = {
    "vibration": 0.28,
    "temperature": 0.25,
    "acoustic_emission": 0.22,
    "current": 0.15,
    "pressure": 0.06,
    "rpm": 0.04
}

# Rolling statistical detection parameters
@dataclass
class AnomalyDetectionConfig:
    """Master configuration for the hybrid anomaly detector."""
    # Rolling window size for moving average and moving std dev
    rolling_window_size: int = 10
    
    # Baseline initialization window (number of initial samples assumed healthy)
    baseline_window_size: int = 30
    
    # Statistical Z-score thresholds
    z_score_warning: float = 3.0
    z_score_critical: float = 4.5
    
    # Minimum physical fraction of normal span required for statistical drift within normal range
    min_span_fraction_drift: float = 0.20
    
    # Delta temperature threshold (Bearing Temp - Ambient Temp) in °C
    delta_t_warning: float = 45.0
    delta_t_critical: float = 58.0
    
    # Machine health score boundaries (0-100 scale)
    risk_threshold_low: float = 20.0
    risk_threshold_medium: float = 45.0
    risk_threshold_high: float = 70.0
    
    # Correlation boost factors
    bearing_syndrome_boost: float = 1.35
    decoupling_boost: float = 1.20


DEFAULT_CONFIG = AnomalyDetectionConfig()
