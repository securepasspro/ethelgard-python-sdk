from .client import SecurePassSDK
from .compliance import ComplianceGenerator

__version__ = "1.0.4-Quantum"

def initialize(api_key, mode="SHADOW", base_url="https://securepasspro.co/api"):
    """
    Initializes the SecurePass Pro SDK with the specified mode.
    The default mode is 'SHADOW' for Aethelgard zero-storage materialization.
    """
    return SecurePassSDK(api_key, base_url=base_url)
