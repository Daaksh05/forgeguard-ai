#!/usr/bin/env python3
"""
ForgeGuard AI - AMD / ROCm Environment Verification Script
===========================================================
This script inspects the local execution environment to verify:
1. Python environment and platform details
2. PyTorch installation
3. ROCm / HIP runtime availability in PyTorch
4. AMD GPU device availability and device specifications
5. Basic tensor compute test on AMD accelerator (if present)

Usage:
    python docs/verify_amd.py
"""

import sys
import platform
import os

def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def main():
    print_header("ForgeGuard AI: AMD/ROCm Environment Verifier")
    
    # 1. Platform Info
    os_name = platform.system()
    os_release = platform.release()
    arch = platform.machine()
    python_ver = sys.version.split()[0]
    
    print(f"[*] Platform OS        : {os_name} ({os_release})")
    print(f"[*] Architecture       : {arch}")
    print(f"[*] Python Version     : {python_ver}")
    print(f"[*] Hostname           : {platform.node()}")

    # 2. PyTorch Check
    print_header("PyTorch & ROCm Detection")
    try:
        import torch
        pytorch_installed = True
        pytorch_version = torch.__version__
        print(f"[+] PyTorch Status     : Installed (v{pytorch_version})")
    except ImportError:
        pytorch_installed = False
        print("[-] PyTorch Status     : NOT INSTALLED")
        print("\n[RESULT] FAILURE: PyTorch is required to run AMD/ROCm workloads.")
        print("To install PyTorch with ROCm support on an AMD host:")
        print("  pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm6.0")
        sys.exit(1)

    # 3. ROCm / HIP Backend Check
    hip_version = getattr(torch.version, 'hip', None)
    cuda_available = torch.cuda.is_available()
    device_count = torch.cuda.device_count() if cuda_available else 0

    if hip_version:
        print(f"[+] ROCm/HIP Version   : {hip_version} (Built with ROCm support)")
    else:
        print("[-] ROCm/HIP Version   : None (Standard PyTorch build without ROCm/HIP)")

    print(f"[*] GPU Available via PyTorch: {'YES' if cuda_available else 'NO'}")
    print(f"[*] GPU Device Count   : {device_count}")

    # 4. Device Enumeration & Inference Smoke Test
    amd_gpu_verified = False

    if cuda_available and device_count > 0:
        print_header("Detected Accelerator Devices")
        for i in range(device_count):
            device_name = torch.cuda.get_device_name(i)
            print(f"  [Device {i}] Name: {device_name}")
            try:
                props = torch.cuda.get_device_properties(i)
                total_mem_gb = props.total_memory / (1024 ** 3)
                print(f"             Total Memory: {total_mem_gb:.2f} GB")
            except Exception as e:
                print(f"             Could not query memory properties: {e}")

        if hip_version is not None:
            amd_gpu_verified = True
            print_header("Smoke Test: Minimal AMD GPU Tensor Operation")
            try:
                device = torch.device("cuda:0")
                x = torch.randn(1024, 1024, device=device)
                y = torch.randn(1024, 1024, device=device)
                z = torch.matmul(x, y)
                torch.cuda.synchronize()
                print(f"[+] Matmul test successful on {torch.cuda.get_device_name(0)}")
                print(f"[+] Tensor shape: {z.shape}, Device: {z.device}")
            except Exception as ex:
                print(f"[-] Tensor computation failed on AMD device: {ex}")
                amd_gpu_verified = False
        else:
            print("\n[!] Warning: CUDA device detected but PyTorch was not built with HIP/ROCm.")
            print("    This may be a non-AMD GPU or standard CUDA environment.")

    # 5. Final Diagnostic Summary
    print_header("Verification Summary")
    if amd_gpu_verified:
        print("[STATUS: SUCCESS] AMD ROCm Environment is fully verified and ready for ForgeGuard AI workloads.")
        sys.exit(0)
    else:
        print("[STATUS: NOT VERIFIED ON CURRENT HOST]")
        print("Reason:")
        if os_name == "Darwin":
            print(" - Current environment is macOS (Darwin).")
            print(" - AMD ROCm drivers and AMD Instinct/Radeon accelerators require a supported Linux host or AMD Developer Cloud instance.")
        elif not hip_version:
            print(" - PyTorch installation does not have ROCm/HIP build enabled.")
        elif not cuda_available:
            print(" - No ROCm-compatible AMD GPU was detected by PyTorch runtime.")
        
        print("\nNext Action for AMD Hackathon Workloads:")
        print(" - Run ForgeGuard AI GPU workloads on AMD Developer Cloud (ADC) or a Linux server with ROCm 6.x installed.")
        print(" - See docs/amd-setup.md for step-by-step AMD Developer Cloud deployment instructions.")
        sys.exit(2)

if __name__ == "__main__":
    main()
