# ForgeGuard AI — AMD & ROCm Environment Setup Guide

> **Hackathon Context**: AMD Developer Hackathon: ACT III (Intelligent Industry Track)  
> **Target Acceleration Infrastructure**: AMD Developer Cloud (ADC) / AMD Instinct Accelerators (MI210 / MI250 / MI300) / AMD ROCm™ 6.x

---

## 1. Overview & Strategy

ForgeGuard AI is an industrial monitoring and predictive maintenance system. It utilizes multimodal AI (visual defect analysis, sensor telemetry anomaly detection, and maintenance manual RAG) which benefits significantly from high-throughput hardware acceleration.

### Development vs. Production/Inference Path
- **Local Development (macOS / Developer Workstations)**: Scaffolding, architecture design, mock pipelines, and code editing. AMD ROCm is Linux-native and cannot run natively on macOS/Apple Silicon.
- **AMD Hardware Workload Execution**: The actual AI models, embedding pipelines, and inference workloads are designed to run on **AMD Developer Cloud (ADC)** or Linux servers with AMD Instinct / Radeon GPUs using ROCm.

---

## 2. Environment Requirements

To run the GPU-accelerated components of ForgeGuard AI, the host system must meet the following prerequisites:

| Component | Recommended Specification |
| :--- | :--- |
| **Platform / Cloud** | AMD Developer Cloud (ADC) or Linux Host |
| **Operating System** | Ubuntu 22.04 LTS / Ubuntu 24.04 LTS or RHEL 9.x |
| **Accelerator Hardware** | AMD Instinct™ (MI210, MI250, MI300X) or AMD Radeon™ PRO (e.g. W7900) |
| **ROCm Stack** | AMD ROCm™ 6.0 / 6.1 / 6.2+ |
| **Python Runtime** | Python 3.10 – 3.11 |
| **PyTorch Framework** | PyTorch with ROCm/HIP support (`torch` with `rocm` wheels) |

---

## 3. Recommended AMD Developer Cloud (ADC) Setup

AMD Developer Cloud provides on-demand access to AMD Instinct accelerators with pre-installed ROCm drivers and optimized PyTorch/vLLM environments.

### Step 3.1: Provision an Instance
1. Log in to the [AMD Developer Cloud Console](https://www.amd.com/en/developer/developer-cloud.html).
2. Select an instance configuration (e.g., **1x AMD Instinct MI210** or **1x AMD Instinct MI250**).
3. Select the pre-configured **PyTorch ROCm** or **Ubuntu ROCm** OS image.
4. Launch the instance and connect via SSH or Web Terminal:
   ```bash
   ssh -i ~/.ssh/your_key.pem ubuntu@<adc-instance-ip>
   ```

### Step 3.2: Clone the Repository
```bash
git clone https://github.com/<org>/forgeguard-ai.git
cd forgeguard-ai
```

### Step 3.3: Set Up Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
```

### Step 3.4: Install PyTorch with ROCm Support
Install the official ROCm PyTorch wheels matching your ROCm driver version (example for ROCm 6.0/6.1):
```bash
# For ROCm 6.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.1
```

---

## 4. ROCm Driver & Device Verification

Verify the system-level AMD ROCm installation:

### Check ROCm System Management Interface (`rocm-smi`)
```bash
rocm-smi
```
*Expected Output*: Displays detected AMD GPUs, temperature, power, VRAM usage, and driver version.

### Check `rocminfo`
```bash
rocminfo | grep -E "(Name|Marketing Name|Compute Unit)"
```
*Expected Output*: Lists the GPU agent name (e.g., `gfx90a` for MI210/MI250, `gfx942` for MI300X).

---

## 5. Automated PyTorch AMD Verification

ForgeGuard AI includes an automated verification script at `docs/verify_amd.py`.

Run the verifier:
```bash
python docs/verify_amd.py
```

### What the script checks:
1. Python environment and platform architecture.
2. PyTorch installation status.
3. ROCm / HIP build availability (`torch.version.hip`).
4. GPU device detection and device count via `torch.cuda.is_available()`.
5. Device properties and VRAM capacity.
6. Execution of a minimal matrix-multiplication smoke test on the AMD device.

---

## 6. Minimal GPU Inference Smoke Test

You can also run a quick inline Python test to confirm HIP/ROCm tensor operations:

```python
import torch

print("ROCm HIP Version:", getattr(torch.version, 'hip', 'Not found'))
print("Is GPU available:", torch.cuda.is_available())

if torch.cuda.is_available():
    device = torch.device("cuda:0")
    print(f"Using device: {torch.cuda.get_device_name(0)}")
    
    # Simple tensor allocation and forward operation
    a = torch.randn(2048, 2048, device=device)
    b = torch.randn(2048, 2048, device=device)
    c = torch.matmul(a, b)
    torch.cuda.synchronize()
    print(f"Tensor computation successful on AMD GPU. Output shape: {c.shape}")
else:
    print("GPU not available via PyTorch.")
```

---

## 7. Containerized ROCm Setup (Docker)

If utilizing Docker on an AMD host, run with access to AMD kernel devices:

```bash
docker run -it \
  --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined \
  --device=/dev/kfd \
  --device=/dev/dri \
  --group-add video \
  --ipc=host \
  --shm-size 8G \
  rocm/pytorch:rocm6.1_ubuntu22.04_py3.10_pytorch_2.1.2 \
  bash
```

---

## 8. Troubleshooting & Common Issues

| Issue | Cause | Resolution |
| :--- | :--- | :--- |
| `torch.cuda.is_available()` returns `False` on Linux | User not in `render`/`video` group | Add user to groups: `sudo usermod -a -G render,video $USER` and relogin. |
| Missing `/dev/kfd` | AMD ROCm kernel module (amdgpu-dkms) not loaded | Run `sudo modprobe amdgpu` or reinstall `amdgpu-dkms`. |
| Architecture mismatch error (`HIP error: no kernel image is available...`) | PyTorch wheel not compiled for GPU ISA (e.g. `gfx90a`) | Set `export HSA_OVERRIDE_GFX_VERSION=9.0.0` or install matching PyTorch ROCm wheel. |
| Running on macOS / Apple Silicon | ROCm is Linux-only | Do not attempt to force ROCm locally. Use AMD Developer Cloud for AI execution. |

---

## 9. How ForgeGuard AI Will Utilize AMD Acceleration

In upcoming phases, the following AI workloads in ForgeGuard AI will execute on AMD infrastructure:

1. **Visual Defect Detection (`ai/vision/`)**:
   - Accelerating convolutional / vision transformer inference for high-frame-rate inspection on industrial camera feeds.
2. **Sensor Telemetry Anomaly Detection (`ai/anomaly_detection/`)**:
   - Fast batch evaluation of multi-sensor time-series embeddings on AMD Instinct compute units.
3. **Maintenance Manual RAG (`ai/rag/`)**:
   - Accelerating vector embedding generation (e.g. with BAAI/BGE or sentence-transformers) and fast semantic similarity search.
4. **Multimodal Agent Reasoning (`ai/agent/`)**:
   - Hosting or accelerating local LLM reasoning models via ROCm-optimized inference engines (e.g., vLLM with ROCm backend).
