#!/usr/bin/env python3

"""
LMFDB Zeta Zeros Reader

This script reads zeta zeros from LMFDB's binary format files and converts them to a
text format suitable for analysis. It implements the exact format described in the
LMFDB source code (platt_zeros.py).

Usage:
  python3 read_lmfdb_zeta.py [input_directory] [output_file] [max_zeros]

Example:
  python3 read_lmfdb_zeta.py data/ zeta_zeros.txt 1000000
"""

import os
import sys
import struct
import math
from pathlib import Path

# Default values
DEFAULT_INPUT_DIR = "data"
DEFAULT_OUTPUT_FILE = "zeta_zeros.txt"
DEFAULT_MAX_ZEROS = 1000000

def read_zeta_zeros(input_dir, output_file, max_zeros=1000000):
    """
    Read zeta zeros from LMFDB binary format files and write them to a text file.
    
    Args:
        input_dir: Directory containing the .dat files
        output_file: Path to output text file
        max_zeros: Maximum number of zeros to extract
    """
    # Ensure input directory exists
    input_path = Path(input_dir)
    if not input_path.exists() or not input_path.is_dir():
        print(f"Error: Input directory {input_dir} does not exist or is not a directory")
        return False
    
    # Find all .dat files in the input directory
    dat_files = sorted([f for f in input_path.glob("*.dat")])
    if not dat_files:
        print(f"Error: No .dat files found in {input_dir}")
        return False
    
    print(f"Found {len(dat_files)} .dat files in {input_dir}")
    
    # Create output directory if it doesn't exist
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Precision for the zeros (as defined in the LMFDB code)
    eps = 2.0 ** (-101)
    
    # Process each file and extract zeros
    total_zeros = 0
    
    with open(output_file, 'w') as out_f:
        for dat_file in dat_files:
            print(f"Processing {dat_file}...")
            
            try:
                with open(dat_file, 'rb') as in_f:
                    # Read number of blocks (first 8 bytes)
                    number_of_blocks = struct.unpack('Q', in_f.read(8))[0]
                    print(f"  File contains {number_of_blocks} blocks")
                    
                    # Process each block
                    for block_number in range(number_of_blocks):
                        # Read block header (32 bytes: 2 doubles + 2 uint64)
                        header = in_f.read(8 * 4)
                        if len(header) < 32:
                            print(f"  Warning: Incomplete header in block {block_number}, skipping")
                            break
                        
                        t0, t1, Nt0, Nt1 = struct.unpack('ddQQ', header)
                        zeros_in_block = Nt1 - Nt0
                        
                        print(f"  Block {block_number}: t0={t0}, t1={t1}, contains {zeros_in_block} zeros")
                        
                        # Process each zero in the block
                        for _ in range(zeros_in_block):
                            # Read 13 bytes for each zero
                            data = in_f.read(13)
                            if len(data) < 13:
                                print(f"  Warning: Incomplete data for zero, skipping")
                                break
                            
                            # Unpack according to LMFDB format
                            z1, z2, z3 = struct.unpack('QIB', data)
                            Z = (z3 << 96) + (z2 << 64) + z1
                            
                            # Calculate the actual zero value
                            zero = t0 + Z * eps
                            
                            # Write to output file
                            out_f.write(f"{zero:.30f}\n")
                            
                            total_zeros += 1
                            if total_zeros % 100000 == 0:
                                print(f"  Processed {total_zeros} zeros")
                            
                            # Stop if we've reached the maximum
                            if total_zeros >= max_zeros:
                                print(f"Reached maximum of {max_zeros} zeros")
                                return True
            
            except Exception as e:
                print(f"Error processing file {dat_file}: {str(e)}")
                continue
    
    print(f"Successfully extracted {total_zeros} zeros to {output_file}")
    return True

def main():
    # Parse command line arguments
    input_dir = DEFAULT_INPUT_DIR
    output_file = DEFAULT_OUTPUT_FILE
    max_zeros = DEFAULT_MAX_ZEROS
    
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    if len(sys.argv) > 3:
        try:
            max_zeros = int(sys.argv[3])
        except ValueError:
            print(f"Warning: Invalid max_zeros value '{sys.argv[3]}', using default {DEFAULT_MAX_ZEROS}")
    
    print(f"Reading zeta zeros from {input_dir} to {output_file} (max: {max_zeros})")
    success = read_zeta_zeros(input_dir, output_file, max_zeros)
    
    if success:
        print("Now you can use the extracted zeros for analysis")
        print(f"Example: python3 zeta_analysis.py {output_file}")
    else:
        print("Failed to extract zeta zeros")

if __name__ == "__main__":
    main()
