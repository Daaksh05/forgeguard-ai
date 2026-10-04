# Vision Module — Computer Vision & Visual Evidence Layer (Phase 5)

> **Module**: `ai/vision`  
> **Status**: Operational Schema & Demo Pipeline (Hardware-Agnostic Interface Ready for AMD ROCm)  
> **Target Machine**: `PUMP_001` (Industrial Centrifugal Pump)

---

## 1. Purpose

The **Computer Vision / Visual Evidence Layer** provides physical inspection verification for ForgeGuard AI. Optical camera feeds inspect asset components (bearing housing, shaft seals, flexible couplings, and baseplates) to detect visible defect signatures that corroborate time-series sensor telemetry and maintenance documentation.

```
+-------------------------------------------------------------------------------+
|                       Optical Camera Inspection Stream                        |
|             (Fixed CCTV, Thermal / Optical Payloads, Inspection Snapshots)     |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                       BaseVisionDetector / Inference API                      |
|                  (ai/vision/inference.py -> detect() interface)               |
+---------------------------------------+---------------------------------------+
                                        |
                    +-------------------+-------------------+
                    |                                       |
                    v                                       v
+---------------------------------------+   +-----------------------------------+
|      Demo Mode / Synthetic Feeds      |   |    AMD ROCm Accelerated Models    |
|   (ai/vision/demo.py [mode: "DEMO"])  |   | (Future: YOLOv8 / ViT on ROCm)    |
+-------------------+-------------------+   +-------------------+---------------+
                    |                                       |
                    +-------------------+-------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                        Structured Visual Evidence Schema                      |
|   - Machine ID, Image ID, Timestamp, Defect Type, Confidence, Severity, Region|
|   - STRICT SEPARATION: OBSERVATION (Visual) vs INTERPRETATION (Implication)   |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                     Multimodal Reasoning Agent (Phase 6)                      |
|          (Cross-modal corroboration: Telemetry + Vision + RAG Manuals)        |
+-------------------------------------------------------------------------------+
```

---

## 2. Visual Evidence Categories

As defined in [`data/visual/visual_dataset_spec.md`](file:///Users/daakshayani/Desktop/ForgeGuard%20AI/data/visual/visual_dataset_spec.md):

| Defect ID | Category Name | Severity | Camera Observation | Domain Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| `NORMAL_OPERATION` | Normal Machine Exterior | `NORMAL` | Intact epoxy coating, dry seal interface, no debris. | Machine operating under nominal conditions. |
| `DEFECT_OIL_LEAK` | Oil / Grease Seal Leakage | `MEDIUM` – `HIGH` | Dark viscous fluid weeping or droplet trails from seal. | Lubricant barrier failure causing grease starvation. |
| `DEFECT_THERMAL_DISCOLOR` | Thermal Paint Blistering | `HIGH` – `CRITICAL` | Severe paint discoloration, charring, and blistering on hub. | Internal bearing friction and surface temp $>85^\circ\text{C}$. |
| `DEFECT_HOUSING_CRACK` | Structural Fatigue Cracks | `CRITICAL` | Linear fissures propagating across pillow block / feet. | Structural cyclic fatigue from extreme vibration ($>7.1\text{ mm/s}$). |
| `DEFECT_SEAL_CONTAMINATION` | Seal Ingress & Wear | `MEDIUM` | Frayed lip seal with dark grit slurry caking around collar. | External particulate ingress accelerating 3-body wear. |
| `DEFECT_COUPLING_WEAR` | Coupling Misalignment & Shredding | `HIGH` | Polyurethane shavings on baseplate with angular offset. | Shaft misalignment imparting severe radial shock loads. |

---

## 3. Visual Evidence Schema & Separation of Concerns

ForgeGuard AI enforces a **strict architectural separation** between what the camera saw (**OBSERVATION**) and what domain physics infers (**INTERPRETATION**):

```json
{
  "machine_id": "PUMP_001",
  "image_id": "IMG_PUMP_001_CRITICAL_003",
  "timestamp": "2026-10-04T15:30:00Z",
  "defect_type": "DEFECT_THERMAL_DISCOLOR",
  "confidence": 0.96,
  "severity": "CRITICAL",
  "region": {
    "x": 0.35,
    "y": 0.28,
    "width": 0.28,
    "height": 0.32
  },
  "visual_evidence": "Severe dark brown and blackened thermal discoloration centered on the cast-iron drive-end bearing housing with visible paint blistering and peeling.",
  "possible_implication": "Prolonged extreme internal heat generation (>90°C surface temperature) from severe metal-to-metal raceway spalling and imminent bearing seizure.",
  "mode": "DEMO"
}
```

### Schema Constraints:
- `confidence`: Verified strictly between `0.0` and `1.0`.
- `severity`: Must belong to `["NORMAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"]`.
- `region`: Non-negative bounding coordinates (`x`, `y`, `width`, `height`).
- `mode`: Explicitly flags `"DEMO"` or `"REAL"`.

---

## 4. Inference Interface (`ai/vision/inference.py`)

A clean, model-independent abstract interface decouples detection callers from underlying model weights:

```python
from ai.vision.inference import detect

# Public inference entry point
report = detect(
    image_path="path/to/inspection_frame.jpg",
    machine_id="PUMP_001",
    timestamp="2026-10-04T15:30:00Z"
)
```

The interface allows plugging in neural backends (e.g. YOLOv8, Faster R-CNN, or Vision Transformers) via `register_backend()` or preloaded weights.

---

## 5. Demo Mode (`ai/vision/demo.py`)

To enable development and testing without downloading heavyweight neural checkpoints or random unverified web images, the demo generator creates verified visual evidence for the synthetic `PUMP_001` failure progression:

```bash
# Run demo for all progressive stages and export JSON
python3 ai/vision/demo.py --scenario all --output results/visual_demo_evidence.json

# Run individual scenarios: 'normal', 'incipient', or 'severe'
python3 ai/vision/demo.py --scenario severe
```

> **CRITICAL**: Every demo evidence object contains `"mode": "DEMO"` and must never be presented as real inference.

---

## 6. Testing

Run the full Phase 5 test suite:
```bash
python3 -m unittest discover -s ai/vision/tests -v
```

---

## 7. Limitations & Future AMD GPU Integration

- **Current Repository State**: No physical imagery or heavy model weights are bundled in the repository.
- **Future AMD ROCm Integration**:
  - When AMD hardware is connected, a fine-tuned vision model (e.g., PyTorch on ROCm or ONNX Runtime with DirectML/MIGraphX) will be registered into `VisionInferenceEngine`.
  - The inference engine will process live camera RTSP streams and generate real-time bounding box visual evidence.
