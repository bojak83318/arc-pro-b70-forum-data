---
type: pkd-answer-key
status: verified
agent-id: gemini-cli-synthesizer
schema: arc-pve-answers-v1
target-hardware: Intel Arc B70 (Battlemage)
target-software: Proxmox VE 8.x/9.x
capabilities: [SR-IOV, vLLM, FFmpeg, Frigate]
last-updated: 2026-04-17T23:45
---

# Intel Arc B70 on Proxmox: The Definitive Setup Guide

> [!summary] Agentic Synthesis
> This artifact provides the direct "Answers" for configuring an Intel Arc B70 (Battlemage) in a Proxmox environment, derived from community testing on Level1Techs.

## 1. SR-IOV (The Multi-VM Unlock)
**Status:** Working (Beta)
- **Kernel Requirement:** Linux Kernel **6.17+** is mandatory for native `xe` driver support with SR-IOV.
- **Driver:** Use the new `xe` driver, NOT the old `i915`.
- **Implementation:**
  - Find device path in `/sys/devices/.../0000:03:00.0`.
  - Enable VFs: `echo 4 > sriov_numvfs`.
  - Proxmox Mapping: Use *Datacenter > Resource Mappings* to add `.1`, `.2`, etc.
- **Critical Note:** You MUST update the B70 firmware in a standalone Windows machine first. Firmware updates fail on VFIO stubs.

## 2. vLLM (AI & LLM Inference)
**Status:** High Performance
- **Benchmark:** Single B70 achieves ~14 tok/s on Qwen 27B (FP8). 4x B70 setup hits **540 tok/s** via tensor parallelism.
- **Recommended CLI:**
  ```bash
  vllm serve /path/to/model --dtype bfloat16 --tensor-parallel-size 4 --max-num-seqs 128 --enforce-eager
  ```
- **Stability:** For 32GB models, set `max-gpu-memory-utilization` to **0.8** to prevent crashes.

## 3. FFmpeg & Frigate (Video Encoding)
**Status:** Ready
- **Driver:** Use `intel-media-driver` (non-free) or `oneVPL`.
- **Frigate Config:**
  ```yaml
  ffmpeg:
    hwaccel_args: preset-intel-qsv-h264 # or h265 for B70
  ```
- **Performance:** The B70 media engine supports AV1 encoding/decoding out of the box. Ensure the LXC or VM has the VF allocated for hardware acceleration.

## 4. Known Issues & "Noise"
- **Code 43:** Still appearing on some Windows VFs; use older drivers (e.g., `32.0.101.8314`) to bypass explorer crashes.
- **Memory:** Native FP8 models may crash on startup; use dynamic Q8 quantization instead for better stability on Battlemage.

---

## Evidence & Traceability
- **Primary Source:** [[b70-primitive.json]]
- **SR-IOV Source:** [[intel-arc-proxmox-sriov-primitive.json]]
- **Key Contributor:** `wendell` (Level1Techs)
