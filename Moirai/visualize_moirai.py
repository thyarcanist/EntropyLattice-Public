#!/usr/bin/env python3
import random
import sys
from pathlib import Path

# --- Determine Paths Relative to This Script ---
SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_DIR_NAME = "Moirai_QuantumBinDemo" # Name of the demo package directory
OUTPUT_IMAGE_NAME = "random_walk_comparison.png"

# --- Configuration ---
NUM_STEPS = 50000  # Number of steps for each walk
ERIS_DATA_FILE = SCRIPT_DIR / DATA_DIR_NAME / "quantum_whitened.bin"
PRNG_SEED = 0      # Seed for the deterministic random generator
OUTPUT_IMAGE_FILE = SCRIPT_DIR / OUTPUT_IMAGE_NAME
PLOT_TITLE = f"2D Random Walk Comparison ({NUM_STEPS:,} steps each)"

# Check if matplotlib is available
try:
    import matplotlib.pyplot as plt
    matplotlib_available = True
except ImportError:
    print("ERROR: matplotlib is required for this script.", file=sys.stderr)
    print("Please install it: pip install matplotlib", file=sys.stderr)
    matplotlib_available = False
    # sys.exit(1) # Exit here if plotting is mandatory

def get_bit_iterator(byte_source):
    """Generator function to yield individual bits from a byte source."""
    for byte in byte_source:
        for i in range(7, -1, -1): # Iterate bits from MSB to LSB
            yield (byte >> i) & 1

def perform_walk(bit_iterator, num_steps):
    """Performs a 2D random walk based on pairs of bits."""
    x, y = 0, 0
    path_x = [0]
    path_y = [0]
    steps_taken = 0

    while steps_taken < num_steps:
        try:
            bit1 = next(bit_iterator)
            bit2 = next(bit_iterator)
            steps_taken += 1

            if bit1 == 0 and bit2 == 0: # 00: Up
                y += 1
            elif bit1 == 0 and bit2 == 1: # 01: Down
                y -= 1
            elif bit1 == 1 and bit2 == 0: # 10: Left
                x -= 1
            elif bit1 == 1 and bit2 == 1: # 11: Right
                x += 1
            else: # Should not happen with 2 bits
                 print("Warning: Unexpected bit combination?", file=sys.stderr)

            path_x.append(x)
            path_y.append(y)

        except StopIteration:
            print(f"Warning: Ran out of bits after {steps_taken} steps (needed {num_steps}).", file=sys.stderr)
            break # Stop if we run out of bits

    return path_x, path_y, steps_taken

def generate_prng_bytes(seed, num_bytes):
    """Generates deterministic pseudo-random bytes."""
    rng = random.Random(seed)
    # Generate bytes efficiently
    return rng.randbytes(num_bytes)


def main():
    if not matplotlib_available:
        print("Exiting due to missing matplotlib library.", file=sys.stderr)
        sys.exit(1)

    print(f"--- Generating Random Walk Comparison ({NUM_STEPS:,} steps) ---")

    # --- Prepare Data Sources ---
    # Eris QRNG Data
    try:
        print(f"Loading Eris data from: {ERIS_DATA_FILE.resolve()}")
        with open(ERIS_DATA_FILE, "rb") as f:
            eris_bytes = f.read()
        print(f"Loaded {len(eris_bytes)} bytes.")
        if len(eris_bytes) * 8 < NUM_STEPS * 2:
            print(f"Warning: Eris data file ({len(eris_bytes)} bytes) might not have enough bits for {NUM_STEPS} steps.", file=sys.stderr)
        eris_bit_iter = get_bit_iterator(eris_bytes)
    except FileNotFoundError:
        print(f"ERROR: Eris data file not found: {ERIS_DATA_FILE.resolve()}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load Eris data: {e}", file=sys.stderr)
        sys.exit(1)

    # Standard PRNG Data
    print(f"Generating PRNG data with seed {PRNG_SEED}...")
    # Calculate required bytes: (NUM_STEPS * 2 bits) / 8 bits/byte, ceiling division
    prng_bytes_needed = (NUM_STEPS * 2 + 7) // 8
    prng_bytes = generate_prng_bytes(PRNG_SEED, prng_bytes_needed)
    print(f"Generated {len(prng_bytes)} PRNG bytes.")
    prng_bit_iter = get_bit_iterator(prng_bytes)

    # --- Perform Walks ---
    print("Performing Eris random walk...")
    eris_path_x, eris_path_y, eris_steps = perform_walk(eris_bit_iter, NUM_STEPS)
    print(f"Eris walk completed {eris_steps} steps.")

    print("Performing PRNG random walk...")
    prng_path_x, prng_path_y, prng_steps = perform_walk(prng_bit_iter, NUM_STEPS)
    print(f"PRNG walk completed {prng_steps} steps.")

    # Ensure we plot based on the minimum steps completed if one ran short
    min_steps = min(eris_steps, prng_steps)
    if min_steps < NUM_STEPS:
         print(f"Plotting based on minimum steps completed: {min_steps}")
    plot_points = min_steps + 1 # +1 because path includes starting point (0,0)

    # --- Plotting ---
    print("Generating plot...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6), sharex=True, sharey=True)
    fig.suptitle(PLOT_TITLE)

    # Eris Plot
    ax1.plot(eris_path_x[:plot_points], eris_path_y[:plot_points], linewidth=0.8, color='blue')
    ax1.set_title(f"Eris QRNG (Seedless)")
    ax1.set_xlabel("X")
    ax1.set_ylabel("Y")
    ax1.plot(eris_path_x[0], eris_path_y[0], 'go') # Start point green
    if plot_points > 1:
        ax1.plot(eris_path_x[plot_points-1], eris_path_y[plot_points-1], 'ro') # End point red
    ax1.set_aspect('equal', adjustable='box') # Make steps visually equal length
    ax1.grid(True, linestyle=':', alpha=0.6)

    # PRNG Plot
    ax2.plot(prng_path_x[:plot_points], prng_path_y[:plot_points], linewidth=0.8, color='orange')
    ax2.set_title(f"Standard PRNG (Seed={PRNG_SEED})")
    ax2.set_xlabel("X")
    # ax2.set_ylabel("Y") # Shared Y axis
    ax2.plot(prng_path_x[0], prng_path_y[0], 'go') # Start point green
    if plot_points > 1:
        ax2.plot(prng_path_x[plot_points-1], prng_path_y[plot_points-1], 'ro') # End point red
    ax2.set_aspect('equal', adjustable='box')
    ax2.grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to prevent title overlap

    # Save the plot
    try:
        plt.savefig(OUTPUT_IMAGE_FILE, dpi=150)
        print(f"Plot saved successfully to: {OUTPUT_IMAGE_FILE.resolve()}")
    except Exception as e:
        print(f"ERROR: Failed to save plot to {OUTPUT_IMAGE_FILE}: {e}", file=sys.stderr)

    # Optionally show the plot
    # plt.show() # Uncomment to display the plot interactively if desired

if __name__ == "__main__":
    main() 