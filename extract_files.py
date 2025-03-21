import os
import gzip
import shutil
import json
import tarfile
import glob

def extract_tarball(tarball_path, extract_folder):
    """Extract the tarball to the specified folder"""
    if not os.path.exists(extract_folder):
        os.makedirs(extract_folder)
    
    print(f"Extracting {tarball_path} to {extract_folder}...")
    with tarfile.open(tarball_path, 'r:gz') as tar:
        tar.extractall(path=extract_folder)
    print("Tarball extraction completed.")

def find_and_extract_gz_files(root_folder, json_destination):
    """
    Recursively find all .gz files in the folder structure,
    extract them to get JSON files, and move JSON files to destination.
    """
    if not os.path.exists(json_destination):
        os.makedirs(json_destination)
    
    # Count for reporting
    gz_count = 0
    json_count = 0
    
    # Walk through all directories recursively
    for current_dir, _, files in os.walk(root_folder):
        # Find all .gz files in current directory
        gz_files = [f for f in files if f.endswith('.gz')]
        
        if gz_files:
            print(f"Found {len(gz_files)} .gz files in: {current_dir}")
            gz_count += len(gz_files)
            
            for gz_file in gz_files:
                gz_path = os.path.join(current_dir, gz_file)
                
                # Temporary path for extracted JSON
                base_name = os.path.splitext(gz_file)[0]
                temp_json_path = os.path.join(current_dir, base_name)
                
                try:
                    # Extract .gz file
                    with gzip.open(gz_path, 'rb') as f_in, open(temp_json_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                    
                    # Create unique name for destination to avoid conflicts
                    # Use parent folder name as prefix
                    parent_folder = os.path.basename(current_dir)
                    dest_json_name = f"{parent_folder}_{base_name}"
                    dest_json_path = os.path.join(json_destination, dest_json_name)
                    
                    # If destination file already exists, add a number
                    counter = 1
                    while os.path.exists(dest_json_path):
                        dest_json_name = f"{parent_folder}_{base_name}_{counter}"
                        dest_json_path = os.path.join(json_destination, dest_json_name)
                        counter += 1
                    
                    # Move JSON file to destination
                    shutil.move(temp_json_path, dest_json_path)
                    
                    # Validate JSON structure
                    try:
                        with open(dest_json_path, 'r', encoding='utf-8') as f:
                            json.load(f)
                        print(f"✓ Successfully extracted and moved: {dest_json_name}")
                        json_count += 1
                    except json.JSONDecodeError:
                        print(f"⚠ Warning: File may not be valid JSON: {dest_json_name}")
                        json_count += 1  # Count it anyway
                
                except Exception as e:
                    print(f"❌ Error processing {gz_file}: {e}")
    
    return gz_count, json_count

if __name__ == "__main__":
    # Set your paths here
    source_tarball = "zips/ndt_ndt7_2025_01_01_20250101T003003.300961Z-ndt7-mlab3-dub01-ndt.tgz"
    extraction_folder = "extracted_tarball"
    json_destination = "extracted_json"
    
    # Step 1: Extract the tarball
    extract_tarball(source_tarball, extraction_folder)
    
    # Step 2: Find and process all .gz files
    print("\nSearching for .gz files and extracting JSON content...")
    gz_found, json_extracted = find_and_extract_gz_files(extraction_folder, json_destination)
    
    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Found {gz_found} .gz files")
    print(f"Extracted {json_extracted} JSON files to: {json_destination}")
    
    if json_extracted > 0:
        print(f"\nAll JSON files have been successfully extracted to: {json_destination}")
    else:
        print("\nNo JSON files were extracted. Please check if the archive contains .gz files.")