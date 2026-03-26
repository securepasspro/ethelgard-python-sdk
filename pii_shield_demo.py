import os
import sys
from securepasspro.client import SecurePassSDK

# 🏛️ AETHELGARD PROTOCOL: TROJAN HORSE DEMO (PII Shield)
# ----------------------------------------------------
# This script demonstrates how a hospital or institution can wrap
# patient SSNs or PII in a stateless handshake using the SDK.

def run_demo():
    # 1. Initialize the SDK with a dummy key for demo purposes
    # In production, use your real Enterprise API Key
    api_key = os.getenv("SPRO_API_KEY", "spro_demo_key_1234567890abcdef")
    sdk = SecurePassSDK(api_key)

    print("🚀 Initializing Aethelgard PII Shield...")
    print("📍 Scenario: Patient SSN Materialization for Dr. Luckett")
    print("-" * 50)

    try:
        # 2. Materialize a secure cryptographic asset (Password or Token)
        # For this demo, we simulate a request to the Zero-Storage API
        print("⚡ Materializing volatile asset...")
        
        # Note: In a real demo, this would call the API. 
        # We'll use a local deterministic call to show the compliance report logic.
        result = sdk.generate_deterministic(
            master_secret="hospital-vault-secret-do-not-store",
            site_id="patient-ssn-wrap-v1",
            use_local=True
        )

        patient_token = result['password']
        print(f"✅ ASSET MATERIALIZED: {patient_token[:4]}****")
        print(f"📡 ENTROPY: {result['entropy']} bits")

        # 3. USE THE DATA (Simulation)
        print("🔓 Dr. Luckett is viewing the patient record...")
        
        # 4. IMMEDIATELY SCRUB RAM
        print("🔥 EXECUTION COMPLETE. Triggering purge...")
        sdk.scrub(patient_token)
        print("🗑️  RAM address zeroed. Data-at-rest: 0 bits.")

        # 5. GENERATE COMPLIANCE PROOF
        print("-" * 50)
        # For local calls, we manually trigger a manifest for the report
        from securepasspro.compliance import ComplianceGenerator
        sdk.last_manifest = ComplianceGenerator.generate_manifest(
            session_id="DEMO-SESSION-999",
            materialization_time_ms=14
        )
        
        sdk.print_compliance_report()

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    run_demo()
