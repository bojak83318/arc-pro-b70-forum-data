---
type: pkd-setup-guide
status: verified
agent-id: gemini-cli-synthesizer
schema: pve-9-setup-v1
target-hardware: Intel Arc B70 / B50 (Battlemage)
target-software: Proxmox VE 9.0
requirements: [Kernel 6.17+, AppArmor Patches, ZFS Patches]
last-updated: 2026-04-17T23:55
---

# Proxmox 9.0 Setup Guide for Intel Battlemage (B70/B50)

> [!warning] Early Adopter Status
> Proxmox 9.0 support for Battlemage SR-IOV requires a custom kernel and patches. This is not yet recommended for production.

## 1. Prerequisites
- **Proxmox VE 9.0 Base:** Ensure you are on a fresh install of PVE 9.x.
- **Kernel Version:** Mandatory upgrade to **Linux Kernel 6.17** (standard PVE 9 kernel is 6.14.x as of late 2025).
- **Firmware:** You **must** update the Arc B70 firmware in a standalone Windows machine before starting. Firmware updates cannot be performed while the card is bound to VFIO.

## 2. Custom Kernel Implementation
Standard PVE kernels lack the necessary `xe` driver support for SR-IOV. 
- **Recommendation:** Use the community-maintained PVE kernel with 6.17 backports.
- **Source:** `github.com/jaminmc/pve-kernel`
- **Installation:**
  1. Download the `.deb` releases from the `jaminmc` repo.
  2. Install via `dpkg -i *.deb`.
  3. Reboot and verify with `uname -a` (Expect: `6.17.0-5.5-pve`).

## 3. Essential Patches
- **AppArmor Fix:** Kernel 6.17 changes AppArmor behavior, causing crashes in Podman/LXC. Apply the "AppArmor 6.14 Compatibility" patch found in the `jaminmc` repository to maintain system stability.
- **ZFS Integration:** Ensure the custom kernel includes the specific ZFS patches required for Proxmox storage stability.

## 4. Enabling SR-IOV on Host
Once on Kernel 6.17, the `xe` driver should be in use:
1. **Verify Driver:** `lspci -k` should show `Kernel driver in use: xe`.
2. **Enable Virtual Functions:**
   ```bash
   # Find your device path
   cd /sys/devices/pci0000:00/.../0000:03:00.0/
   # Enable 4 VFs
   echo 4 > sriov_numvfs
   ```
3. **Verify VFs:** `lspci` should now show four additional "VGA compatible controller" entries.

---

## Evidence & Traceability
- **Primary Source:** [[intel-arc-proxmox-sriov-primitive.json]]
- **Key Implementation Contributor:** `jaminmc`
- **Validation Contributor:** `wendell`
