import hashlib
import argparse
import re
from pathlib import Path
import sys

# Define expected filenames
VERIFICATION_FILENAME = "verification.txt"
RAW_DATA_FILENAME = "quantum_raw.bin"
WHITENED_DATA_FILENAME = "quantum_whitened.bin"

def calculate_sha256(file_path: Path) -> str:
    """Calculates the SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        print(f"ERROR: File not found for hashing: {file_path}", file=sys.stderr)
        return ""
    except IOError as e:
        print(f"ERROR: Could not read file for hashing: {file_path} ({e})", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"ERROR: Unexpected error hashing file {file_path}: {e}", file=sys.stderr)
        return ""

def parse_verification_file(verif_path: Path) -> dict:
    """Parses the verification.txt file to extract expected SHA256 hashes."""
    expected_hashes = {
        "raw": None,
        "whitened": None
    }
    try:
        # Read with universal newline support
        with open(verif_path, 'r', newline=None) as f:
            content = f.read()

        # *** Regex Patterns ***
        # Look for "Raw Data SHA-256: <hash>" or "SHA-256 (Raw): <hash>" for flexibility
        raw_match = re.search(r"(?:Raw Data SHA-256|SHA-256 \(Raw\)):\s*([a-f0-9]{64})", content, re.IGNORECASE | re.MULTILINE)
        # Look for "Whitened Data SHA-256: <hash>" or "SHA-256 (Whitened): <hash>"
        whitened_match = re.search(r"(?:Whitened Data SHA-256|SHA-256 \(Whitened\)):\s*([a-f0-9]{64})", content, re.IGNORECASE | re.MULTILINE)
        # ***************************

        if raw_match:
            expected_hashes["raw"] = raw_match.group(1).lower()
            print(f"INFO: Found expected Raw SHA256: {expected_hashes['raw']}")
        else:
            print(f"WARNING: Expected Raw SHA256 hash not found in {verif_path}.")

        if whitened_match:
            expected_hashes["whitened"] = whitened_match.group(1).lower()
            print(f"INFO: Found expected Whitened SHA256: {expected_hashes['whitened']}")
        else:
            # It's essential to have the whitened hash
            print(f"ERROR: Expected Whitened SHA256 hash not found in {verif_path}.", file=sys.stderr)
            # Return None or raise error if whitened hash is mandatory
            return {} # Indicate failure to parse essential info

    except FileNotFoundError:
        print(f"ERROR: Verification file not found: {verif_path}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"ERROR: Failed to read or parse {verif_path}: {e}", file=sys.stderr)
        return {}

    return expected_hashes

def main():
    parser = argparse.ArgumentParser(
        description="Verify the integrity of an Eris QRNG data package using SHA256 hashes.",
        epilog=f"Example: python verify_package_integrity.py path/to/quantum_package_directory"
    )
    parser.add_argument(
        "package_dir",
        type=str,
        help="Path to the directory containing the quantum data package (verification.txt, quantum_raw.bin, quantum_whitened.bin)."
    )
    args = parser.parse_args()

    package_path = Path(args.package_dir)

    if not package_path.is_dir():
        print(f"ERROR: Provided path is not a valid directory: {package_path}", file=sys.stderr)
        sys.exit(1)

    print(f"--- Verifying Package Integrity: {package_path.name} ---")

    # --- File Paths ---
    verification_file = package_path / VERIFICATION_FILENAME
    raw_data_file = package_path / RAW_DATA_FILENAME
    whitened_data_file = package_path / WHITENED_DATA_FILENAME

    # --- Check for essential files ---
    if not verification_file.exists():
        print(f"ERROR: Essential file '{VERIFICATION_FILENAME}' not found in {package_path}", file=sys.stderr)
        sys.exit(1)
    if not whitened_data_file.exists():
        print(f"ERROR: Essential file '{WHITENED_DATA_FILENAME}' not found in {package_path}", file=sys.stderr)
        sys.exit(1)

    has_raw_file = raw_data_file.exists()
    if not has_raw_file:
         print(f"INFO: Optional file '{RAW_DATA_FILENAME}' not found. Skipping raw data check.")


    # --- Parse Expected Hashes ---
    print(f"\n[1] Parsing {VERIFICATION_FILENAME}...")
    expected_hashes = parse_verification_file(verification_file)
    if not expected_hashes or not expected_hashes.get("whitened"): # Ensure whitened hash was found
        print(f"ERROR: Could not parse required hashes from {verification_file}. Aborting.", file=sys.stderr)
        sys.exit(1)

    # --- Calculate Actual Hashes ---
    print("\n[2] Calculating actual file hashes...")
    actual_hashes = {
        "raw": None,
        "whitened": None
    }

    # Calculate whitened hash (mandatory)
    actual_hashes["whitened"] = calculate_sha256(whitened_data_file)
    if not actual_hashes["whitened"]:
        print(f"ERROR: Failed to calculate hash for {whitened_data_file}. Aborting.", file=sys.stderr)
        sys.exit(1)
    print(f"  Calculated Whitened SHA256: {actual_hashes['whitened']}")

    # Calculate raw hash (optional)
    if has_raw_file and expected_hashes.get("raw"): # Only calculate if raw file exists AND expected hash was found
        actual_hashes["raw"] = calculate_sha256(raw_data_file)
        if not actual_hashes["raw"]:
             print(f"ERROR: Failed to calculate hash for {raw_data_file}. Raw check will fail.", file=sys.stderr)
             # Allow script to continue to check whitened file
        else:
             print(f"  Calculated Raw SHA256:       {actual_hashes['raw']}")
    elif has_raw_file and not expected_hashes.get("raw"):
         print(f"  INFO: Raw file exists but no expected hash found in verification file. Cannot check.")
    elif not has_raw_file and expected_hashes.get("raw"):
         print(f"  WARNING: Expected raw hash found but raw file does not exist. Cannot check.")


    # --- Compare Hashes ---
    print("\n[3] Comparing Hashes...")
    results = {"overall": "PASS"} # Assume pass initially

    # Compare Whitened (Mandatory)
    if expected_hashes["whitened"] == actual_hashes["whitened"]:
        print(f"  Whitened Data ({WHITENED_DATA_FILENAME}): MATCH -> PASS")
    else:
        print(f"  Whitened Data ({WHITENED_DATA_FILENAME}): MISMATCH -> FAIL")
        print(f"    Expected: {expected_hashes['whitened']}")
        print(f"    Actual:   {actual_hashes['whitened']}")
        results["overall"] = "FAIL"

    # Compare Raw (Optional - only if expected and actual are available)
    if expected_hashes.get("raw") and actual_hashes.get("raw"):
        if expected_hashes["raw"] == actual_hashes["raw"]:
            print(f"  Raw Data      ({RAW_DATA_FILENAME}): MATCH -> PASS")
        else:
            print(f"  Raw Data      ({RAW_DATA_FILENAME}): MISMATCH -> FAIL")
            print(f"    Expected: {expected_hashes['raw']}")
            print(f"    Actual:   {actual_hashes['raw']}")
            results["overall"] = "FAIL" # Fail overall if raw mismatch occurs when expected
    elif expected_hashes.get("raw") and not has_raw_file:
         print(f"  Raw Data      ({RAW_DATA_FILENAME}): SKIPPED (File not found)")
         # Don't fail overall if optional raw file is missing but expected hash existed
    elif expected_hashes.get("raw") and has_raw_file and not actual_hashes.get("raw"):
         print(f"  Raw Data      ({RAW_DATA_FILENAME}): SKIPPED (Hashing failed)")
         results["overall"] = "FAIL" # Fail if hashing failed for existing file
    elif not expected_hashes.get("raw"):
        print(f"  Raw Data      ({RAW_DATA_FILENAME}): SKIPPED (Not specified in verification file)")


    # --- Final Result ---
    print(f"\n--- Overall Package Integrity Verification: {results['overall']} ---")

    if results["overall"] == "FAIL":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main() 