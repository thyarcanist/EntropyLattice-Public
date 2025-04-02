#!/usr/bin/env python3
import hashlib
from pathlib import Path
import sys

# Path to the quantum data file relative to the *workspace root*
QUANTUM_DATA_PATH = Path("./Moirai/Moirai_QuantumBinDemo/quantum_whitened.bin")

# Load the quantum random data
print(f"Attempting to load data from: {QUANTUM_DATA_PATH.resolve()}")
try:
    with open(QUANTUM_DATA_PATH, "rb") as f:
        quantum_data = f.read()
    print(f"Successfully loaded {len(quantum_data)} bytes from {QUANTUM_DATA_PATH}")
except FileNotFoundError:
    print(f"ERROR: File not found: {QUANTUM_DATA_PATH.resolve()}", file=sys.stderr)
    print("Ensure the script is run from the 'Moirai' directory or adjust the path.", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Failed to load quantum data from {QUANTUM_DATA_PATH}: {e}", file=sys.stderr)
    sys.exit(1)

# --- Helper function from example --- 
# Make it available globally for all examples in this script
def get_random_key(position, length=32):
    """Extracts bytes from the loaded quantum data."""
    if position < 0:
        print(f"Warning: Negative position ({position}) is invalid. Using position 0.")
        position = 0
        
    if position >= len(quantum_data):
        print(f"Warning: Start position ({position}) is beyond data length ({len(quantum_data)}). Returning empty bytes.")
        return b''
        
    end_position = position + length
    if end_position > len(quantum_data):
        print(f"Warning: Requested range ({position} to {end_position}) exceeds data length ({len(quantum_data)}). Truncating.")
        return quantum_data[position:] # Return available data from position
        
    return quantum_data[position:end_position]

print("\n--- Testing Example 1: Generating Cryptographic Keys ---")
example1_ok = False
try:
    key_pos = 1024
    key_len = 32
    secure_key = get_random_key(key_pos, key_len)
    if len(secure_key) == key_len:
        print(f"Generated key ({len(secure_key)} bytes) starting with: {secure_key[:8].hex()}...")
        print("Example 1: OK")
        example1_ok = True
    elif len(secure_key) > 0:
        print(f"Example 1: FAIL (Incorrect key length: {len(secure_key)}, expected {key_len} - likely due to EOF)")
    else:
        print(f"Example 1: FAIL (Generated empty key - position {key_pos} likely out of bounds?)")
except Exception as e:
    print(f"Example 1: FAIL (Error: {e})")


print("\n--- Testing Example 2: One-Time Pad Encryption ---")
example2_ok = False
try:
    def xor_encrypt(message, key):
        # Ensure key is at least as long as message for OTP
        if len(key) < len(message):
             raise ValueError("Key length must be >= message length for OTP")
        # Use only the part of the key that matches the message length
        return bytes(a ^ b for a, b in zip(message, key[:len(message)]))

    message = b"SECURE MESSAGE"
    otp_pos = 2048
    otp_len = len(message)
    key_otp = get_random_key(otp_pos, otp_len)

    if len(key_otp) == otp_len:
        encrypted = xor_encrypt(message, key_otp)
        decrypted = xor_encrypt(encrypted, key_otp)
        print(f"Original:  {message.decode()}")
        print(f"Encrypted: {encrypted.hex()}")
        print(f"Decrypted: {decrypted.decode()}")
        if decrypted == message:
            print("Example 2: OK")
            example2_ok = True
        else:
            print("Example 2: FAIL (Decryption mismatch)")
    else:
        print(f"Example 2: FAIL (Could not get OTP key of required length {otp_len} at pos {otp_pos})")
except ValueError as ve:
     print(f"Example 2: FAIL (ValueError: {ve})")
except Exception as e:
    print(f"Example 2: FAIL (Error: {e})")


print("\n--- Testing Example 3: Generating Random Bitcoin Wallet ---")
example3_ok = False
try:
    # Requires: pip install bitcoin
    from bitcoin import privtopub, pubtoaddr
    bitcoin_lib_found = True
except ImportError:
    bitcoin_lib_found = False
    print("INFO: 'bitcoin' library not installed. Skipping Example 3 execution.")

if bitcoin_lib_found:
    try:
        btc_pos = 3072
        btc_len = 32 # Bitcoin private keys are 256 bits (32 bytes)
        private_key_bytes = get_random_key(btc_pos, btc_len)

        if len(private_key_bytes) == btc_len:
            private_key_hex = private_key_bytes.hex()
            # Basic validation: Check if key is 0 or >= curve order 'n'
            # n = 115792089237316195423570985008687907852837564279074904382605163141518161494337
            n_hex = "fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141"
            n_int = int(n_hex, 16)
            key_int = int(private_key_hex, 16)
            
            if key_int == 0 or key_int >= n_int:
                 print(f"Example 3: FAIL (Generated invalid Bitcoin private key: {private_key_hex})")
            else:
                public_key = privtopub(private_key_hex)
                address = pubtoaddr(public_key)
                print(f"Bitcoin Private Key (hex, partial): {private_key_hex[:8]}...{private_key_hex[-8:]}")
                print(f"Generated Bitcoin Address: {address}")
                print("Example 3: OK (Address generated, visually check format)")
                example3_ok = True
        else:
             print(f"Example 3: FAIL (Could not get private key of required length {btc_len} at pos {btc_pos})")

    except Exception as e:
        print(f"Example 3: FAIL (Error during execution: {e})")
else:
    print("Example 3: SKIPPED (Required 'bitcoin' library not installed)")

print("\n--- Python Tests Summary ---")
print(f"Example 1 (Keys):       {'PASS' if example1_ok else 'FAIL'}")
print(f"Example 2 (OTP):        {'PASS' if example2_ok else 'FAIL'}")
print(f"Example 3 (Bitcoin):    {'PASS' if example3_ok else ('FAIL' if bitcoin_lib_found else 'SKIPPED')}") 