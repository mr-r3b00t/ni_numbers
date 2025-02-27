import itertools
import string
import concurrent.futures
import threading
import os
from tqdm import tqdm

# Thread-safe counter for tracking total NINOs generated
count_lock = threading.Lock()
total_count = 0

def generate_ninos_for_prefix(prefix, progress_bar):
    """Generate all NINOs for a given prefix and write to a file."""
    global total_count
    digits = string.digits
    final_letters = 'ABCD'
    prefix_str = ''.join(prefix)
    
    # Skip invalid combinations
    if prefix_str in ['BG', 'GB', 'NK', 'KN', 'TN', 'NT', 'ZZ']:
        return 0
    
    local_count = 0
    output_file = f'ninos_{prefix_str}.txt'
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'a') as f:
        for num in itertools.product(digits, repeat=6):
            num_str = ''.join(num)
            for suffix in final_letters:
                nino = f"{prefix_str}{num_str}{suffix}"
                f.write(nino + '\n')
                local_count += 1
    
    # Update global counter and progress bar safely
    with count_lock:
        total_count += local_count
        progress_bar.update(local_count)
    
    return local_count

def generate_ninos_multithreaded(max_workers=4):
    """Generate all NINOs using multiple threads with a progress bar."""
    # Valid letters for prefix
    first_letters = [l for l in string.ascii_uppercase if l not in 'DFIQUV']
    second_letters = [l for l in string.ascii_uppercase if l not in 'DFIQUVO']
    
    # All possible prefixes
    prefixes = list(itertools.product(first_letters, second_letters))
    total_combinations = len(prefixes) * (10**6) * 4  # 10^6 digits, 4 final letters
    
    print(f"Total possible combinations: {total_combinations:,}")
    print(f"Using {max_workers} threads to process {len(prefixes)} prefixes.")
    
    # Initialize progress bar
    with tqdm(total=total_combinations, desc="Generating NINOs", unit="NINOs") as pbar:
        # Use ThreadPoolExecutor to process prefixes in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tasks for each prefix
            future_to_prefix = {
                executor.submit(generate_ninos_for_prefix, prefix, pbar): prefix 
                for prefix in prefixes
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_prefix):
                prefix = future_to_prefix[future]
                try:
                    local_count = future.result()
                    # Uncomment to log per-prefix completion
                    # print(f"Finished prefix {''.join(prefix)}: {local_count:,} NINOs")
                except Exception as e:
                    print(f"Prefix {''.join(prefix)} generated an error: {e}")
    
    print(f"Finished! Total generated: {total_count:,}")
    print(f"NINOs written to files: ninos_AA.txt, ninos_AB.txt, etc.")

# Run the multithreaded generator
if __name__ == "__main__":
    generate_ninos_multithreaded(max_workers=4)  # Adjust max_workers as needed
