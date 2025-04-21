# save as fix_zeta_format.py
import os

# Configuration
DATA_DIR = "data"
OUTPUT_FILE = "data/clean_zeta_zeros.txt"

def examine_and_fix_zeta_files():
    """
    Examines the format of zeta zeros files and creates a clean version
    """
    # List of input files
    input_files = [
        os.path.join(DATA_DIR, "zeros_100000.dat"),
        os.path.join(DATA_DIR, "zeros_236000.dat"),
        os.path.join(DATA_DIR, "zeros_446000.dat"),
        os.path.join(DATA_DIR, "zeros_674000.dat")
    ]
    
    # Examine first few lines of first file to understand format
    print(f"Examining format of {input_files[0]}...")
    with open(input_files[0], 'r') as f:
        first_lines = [f.readline() for _ in range(5)]
    
    print("First 5 lines of the file:")
    for i, line in enumerate(first_lines):
        print(f"Line {i+1}: '{line.strip()}' (length: {len(line.strip())})")
    
    # Process all files and create a clean version
    print(f"\nProcessing all files and creating clean version at {OUTPUT_FILE}...")
    total_zeros = 0
    
    with open(OUTPUT_FILE, 'w') as out_f:
        for input_file in input_files:
            print(f"Processing {input_file}...")
            with open(input_file, 'r') as in_f:
                for line in in_f:
                    # Clean the line - strip whitespace and any non-numeric characters
                    clean_line = line.strip()
                    
                    # Try to convert to float to verify it's a valid number
                    try:
                        value = float(clean_line)
                        out_f.write(f"{value}\n")
                        total_zeros += 1
                        
                        # Limit to 1 million zeros
                        if total_zeros >= 1000000:
                            print(f"Reached 1 million zeros, stopping.")
                            break
                    except ValueError:
                        print(f"Warning: Skipping invalid line: '{clean_line}'")
            
            # Stop if we've reached 1 million zeros
            if total_zeros >= 1000000:
                break
    
    print(f"Successfully created clean file with {total_zeros} zeros")
    print(f"You can now use this file for analysis: {OUTPUT_FILE}")

if __name__ == "__main__":
    examine_and_fix_zeta_files()
