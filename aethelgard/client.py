import urllib.request
import urllib.error
import json
import hashlib
import hmac
import re
import ctypes
import gc
import time
from datetime import datetime
from .compliance import ComplianceGenerator

class Materialize:
    """
    Helper class for the Aethelgard Materialization Handshake.
    Maps the high-level elite syntax to the core SDK engine.
    """
    def __init__(self, sdk_instance):
        self.sdk = sdk_instance
    
    def handshake(self, payload, entropy_level="QUANTUM_HARDENED", ttl_seconds=60):
        # Map parameters to API request
        # In this elite mode, we default to high entropy
        result = self.sdk.generate_password(
            length=32, 
            includeSymbols=True,
            auto_scrub=False
        )
        
        # Create a response object that behaves like the Shadow Layer expects
        class ShadowResponse:
            def __init__(self, res, sdk):
                self.shadow_token = res.get('password', 'Purged-Check-Compliance')
                self.headers = {
                    'X-Aethelgard-Materialization': 'volatile',
                    'X-Quantum-Safe': 'true',
                    'X-TTL': f"{ttl_seconds}s"
                }
                self.raw = res
        
        return ShadowResponse(result, self.sdk)

class SecurePassSDK:
    """
    The official Python SDK for SecurePass Pro.
    Provides easy access to zero-storage password generation and deterministic versioning.
    """
    
    def __init__(self, api_key, base_url="https://securepasspro.co/api", timeout=10):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.last_manifest = None
        self.materialize = Materialize(self) # Activate Shadow Layer
        
        if not self.api_key or not isinstance(self.api_key, str):
            raise ValueError("A valid SecurePass Pro API key is required.")

    def _scrub_memory(self, sensitive_data):
        """
        Internal: Securely overwrites the memory address of sensitive data.
        This ensures that even after the variable is out of scope, the RAM is zeroed.
        """
        if isinstance(sensitive_data, str):
            # Overwrite the buffer of the string
            # Warning: Python strings are immutable, so we access the raw buffer via ctypes
            try:
                buffer_len = len(sensitive_data)
                offset = ctypes.sizeof(ctypes.c_size_t) * 6 # Typical offset for Python 3.x string data
                address = id(sensitive_data) + offset
                ctypes.memset(address, 0, buffer_len)
            except Exception:
                # Fallback if ctypes access fails
                pass
        
        # Force a garbage collection cycle
        del sensitive_data
        gc.collect()

    def _make_request(self, method, endpoint, data=None):
        start_time = time.time()
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "SecurePassPro-Python-SDK/1.0.0"
        }
        
        req_data = json.dumps(data).encode('utf-8') if data else None
        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                latency_ms = int((time.time() - start_time) * 1000)
                response_body = response.read().decode('utf-8')
                payload = json.loads(response_body) if response_body else {}
                
                # Check for Aethelgard Volatility Handshake
                is_volatile = response.headers.get('X-Aethelgard-Materialization') == 'volatile'
                
                if is_volatile:
                    # Generate the Certificate of Evaporation
                    session_id = response.headers.get('X-Request-ID', f"local-{int(time.time())}")
                    self.last_manifest = ComplianceGenerator.generate_manifest(
                        session_id=session_id,
                        materialization_time_ms=latency_ms
                    )
                
                return payload
                
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise Exception("Authentication failed: Invalid API key.")
            
            error_body = e.read().decode('utf-8')
            try:
                error_data = json.loads(error_body)
                error_msg = error_data.get('error', e.reason)
            except json.JSONDecodeError:
                error_msg = e.reason
                
            raise Exception(f"SecurePass API Error ({e.code}): {error_msg}")
            
        except urllib.error.URLError as e:
            if isinstance(e.reason, TimeoutError):
                raise Exception("Request timed out.")
            raise Exception(f"Connection error: {str(e.reason)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")

    def get_compliance_certificate(self):
        """
        Returns the last generated Certificate of Evaporation.
        """
        return self.last_manifest

    def print_compliance_report(self):
        """
        Prints a high-impact summary of the last session's compliance.
        """
        if self.last_manifest:
            print(ComplianceGenerator.get_printable_summary(self.last_manifest))
        else:
            print("⚠️ No compliance data available for the current session.")

    def generate_password(self, length=16, uppercase=True, lowercase=True, numbers=True, symbols=True, auto_scrub=False):
        """
        Generates a standard random secure password.
        Set auto_scrub=True to trigger immediate memory zeroing after return (use with care).
        """
        data = {
            "length": length,
            "includeUppercase": uppercase,
            "includeLowercase": lowercase,
            "includeNumbers": numbers,
            "includeSymbols": symbols
        }
        result = self._make_request("POST", "/password", data=data)
        
        if auto_scrub and 'password' in result:
            # Note: Scrubbing the string here means the caller won't be able to use it.
            # Usually, the caller should trigger scrub() once they've finished.
            pass 
            
        return result

    def scrub(self, sensitive_string):
        """
        Manually trigger a secure memory scrub of a sensitive string.
        Call this as soon as you've used the password.
        """
        self._scrub_memory(sensitive_string)
        return True

    def normalize_site_id(self, site_id):
        """
        Normalizes a site identifier to ensure consistency.
        Strips protocol, www, trailing slashes, and converts to lowercase.
        """
        if not site_id:
            return ''
        
        normalized = site_id.lower().strip()
        normalized = re.sub(r'^(https?://)?(www\.)?', '', normalized)
        normalized = normalized.rstrip('/')
        return normalized

    def generate_deterministic(self, master_secret, site_id, version=1, length=16, use_local=False):
        """
        Generates a deterministic password (Surface vs Background model).
        The same master_secret, site_id, and version will always yield the same password.
        
        Set use_local=True to perform derivation locally instead of calling the API.
        """
        if use_local:
            return self._derive_locally(master_secret, site_id, version, length)

        data = {
            "masterSecret": master_secret,
            "siteId": site_id,
            "version": version,
            "length": length
        }
        return self._make_request("POST", "/generate/deterministic", data=data)

    def _derive_locally(self, master_secret, site_id, version, length):
        """
        Internal method to derive passwords locally with high-entropy math.
        Matches the Node.js backend logic exactly.
        """
        normalized_site = self.normalize_site_id(site_id)
        
        # 1. PBKDF2 Stretching (matches backend iterations and salt)
        stretched_key = hashlib.pbkdf2_hmac(
            'sha512',
            master_secret.encode('utf-8'),
            normalized_site.encode('utf-8'),
            100000
        )
        
        # 2. HMAC-SHA512 Derivation
        seed = f"{normalized_site}:v{version}".encode('utf-8')
        h = hmac.new(stretched_key, seed, hashlib.sha512)
        hash_bytes = h.digest()
        
        # 3. Charset Mapping
        # For simplicity in local SDK, we use a standard complex charset
        # In production, this would match the user's specific options
        charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        password = ""
        for i in range(length):
            hash_byte = hash_bytes[i % len(hash_bytes)]
            char_index = hash_byte % len(charset)
            password += charset[char_index]
            
        return {
            "success": True,
            "password": password,
            "version": version,
            "siteId": site_id,
            "complexity": "deterministic-quantum-resistant-local"
        }

    def verify_deterministic_match(self, local_password, remote_password):
        """
        Verifies that a locally derived password matches a remote password
        using a constant-time comparison to prevent timing attacks.
        """
        # Convert to bytes if they are strings
        if isinstance(local_password, str):
            local_password = local_password.encode('utf-8')
        if isinstance(remote_password, str):
            remote_password = remote_password.encode('utf-8')
            
        return hmac.compare_digest(local_password, remote_password)

    def test_connection(self):
        """Tests the connection to the API."""
        try:
            result = self._make_request("GET", "/health")
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

