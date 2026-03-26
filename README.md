# Aethelgard Protocol Python SDK

The official Python library for the [Aethelgard Protocol](https://securepasspro.co) Zero-Storage Password Infrastructure.

## Features

- **Zero-Storage Generation**: Generate cryptographically secure passwords without storing them.
- **Deterministic Versioning**: Implement the "Surface vs Background" model. Rotate passwords by simply incrementing a version number.
- **Automated Rotation**: Perfectly suited for backend scripts and server-side automation.

## Installation

```bash
pip install aethelgard-sdk
```

> **Note for Enterprise Architects:** The Aethelgard Python SDK is a **zero-dependency primitive**. It utilizes only the Python Standard Library (`urllib`, `ctypes`, `hmac`), eliminating third-party supply chain risks entirely.

## Quick Start

### Basic Usage

```python
from aethelgard import SecurePassSDK

# Initialize with your API key (provisioned in the Command Dashboard)
sdk = SecurePassSDK("spro_your_api_key_here")

# Generate a strong ephemeral password
result = sdk.generate_password(length=24, symbols=True)
print(f"Generated: {result['password']}")
```

### Deterministic Generation (Recommended for Rotation)

This is the preferred pattern for password management under the Aethelgard Protocol. The same inputs always produce the same output, allowing zero-persistent rotation.

```python
master_secret = "your_high_entropy_master_secret_here"
site_id = "google.com"

# In production Guardian/Sovereign Nodes, the master_secret never leaves the atomic 14.2ms liquidation window

# Version 1 — Current password
v1 = sdk.generate_deterministic(master_secret, site_id, version=1)
print(f"Version 1: {v1['password']}")

# Version 2 — After breach, compromise, or scheduled rotation (e.g., 90 days)
v2 = sdk.generate_deterministic(master_secret, site_id, version=2)
print(f"Version 2: {v2['password']}")
```

> **Threat Model Note:** This approach ensures that even if the Background secret is compromised later, past Surface passwords remain mathematically independent.

## Verification

Run the included test suite to validate installation and deterministic behavior:

```bash
python scripts/test-python-sdk.py
```

## Security

- **Constant-Time Comparison:** Password/key verification uses `hmac.compare_digest()` to eliminate timing attacks — required for high-assurance environments.
- **Deterministic Derivation:** Powered by HMAC-SHA512. Surface passwords (what you use on sites) are mathematically decoupled from the Background master secret, aligning with Forensic Nullity principles: derive what you need, liquidate the rest.

## Integration with Aethelgard Nodes

For full Forensic Nullity flows, the SDK integrates directly with the Sovereign Command API. When executing `generate_deterministic` or `generate_password`, the production node utilizes an Atomic Kernel Syscall (eBPF/LKM) to eliminate intermediate observable states, achieving near-zero latency (<0.1ms).

## Support

For Guardian Tier or Sovereign Node support, contact admin@securepasspro.co or access your Command Dashboard.
