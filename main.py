import os
import re
import sys
import time
import base64

start_time = time.time()

# Usage
def print_usage():
    print("Usage:")
    print("  python my_script.py encode <folder_path> <output_dir> <output_file_name>")
    print("  python my_script.py decode <data.txt> <output_path>")
    print("\nOptions:")
    print("  encode <folder_path> <output_dir> <output_file_name>     Path to the folder to be encoded and where to save the output file")
    print("  decode <data.txt> <output_path>                           Decode Base64 data from the specified file and reconstruct images to output_path")

# Some Vars
bucket_number = 0
number_of_files = 0

# Directory and output configuration
try:
    option = sys.argv[1].lower()
except IndexError:
    print(f"Please Provide us with some operation [Encode/Decode] See Usage Below")
    print_usage()
    sys.exit()

if option == "encode" or option == "decode":
    try:
        IN_DIR = sys.argv[2]
    except IndexError:
        print(f"Please Provide us With some paths to Take data from")
        sys.exit()

OUT_IMAGE_DIR = './Output'

def check_file_extension(filename, extension):
    pattern = rf".*\.{extension}$"
    return bool(re.match(pattern, filename, re.IGNORECASE))


def encode_images(folder_path, output_dir, bucket_size_gb):
    global bucket_number, number_of_files  # Declare global variables
    bucket_size_bytes = bucket_size_gb * (1024 ** 3)  # Convert GB to bytes
    number_of_files = 0

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        if os.path.isfile(file_path):
            try:
                # Reset the bucket number for each new file
                bucket_number = 1
                print(f"Encoding file: {filename}")
                
                with open(file_path, 'rb') as image_file:
                    # Encode the file to base64
                    file_base_name, file_extension = os.path.splitext(filename)
                    encoded_data = file_base_name+file_extension + ':' + base64.b64encode(image_file.read()).decode('utf-8')

                    # Initialize the data pointer
                    data_written = 0

                    # Write the encoded data in buckets
                    while data_written < len(encoded_data):
                        remaining_data = encoded_data[data_written:]
                        remaining_size = len(remaining_data)

                        # Construct the output file name with the bucket number
                        output_file_path = os.path.join(output_dir, f"{file_base_name}_{bucket_number}.txt")
                        
                        # Open the bucket file for writing
                        with open(output_file_path, 'w') as output_file_handle:
                            if remaining_size > bucket_size_bytes:
                                # If the remaining data is larger than the bucket size, split it
                                output_file_handle.write(remaining_data[:bucket_size_bytes])
                                data_written += bucket_size_bytes
                            else:
                                # Otherwise, write the remaining data
                                output_file_handle.write(remaining_data)
                                data_written += remaining_size
                        
                        print(f"Written to: {output_file_path}")

                        # If there is still data left, move to the next bucket
                        if data_written < len(encoded_data):
                            bucket_number += 1

                number_of_files += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print(f"Total files encoded: {number_of_files}")


def decode_images(encoded_dir, output_dir):
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Loop through all files in the encoded directory
        for filename in os.listdir(encoded_dir):
            file_path = os.path.join(encoded_dir, filename)
            
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r') as infile:
                        print(f"Decoding file: {filename}")
                        # Read all lines in the file
                        encoded_data = infile.read().strip()

                        # Check if this is the first part of the file (contains filename)
                        if filename.endswith('_1.txt'):
                            # The first part contains the filename in the format `filename:encodedData`
                            file_name, encoded_string = encoded_data.split(':', 1)
                            print(f"Decoding -> '{file_name}'")
                            decoded_data = base64.b64decode(encoded_string)
                            
                            # Open the file for writing the decoded data
                            output_file_path = os.path.join(output_dir, f"reconstructed_{file_name}")
                            with open(output_file_path, 'wb') as outfile:
                                outfile.write(decoded_data)
                        else:
                            # Subsequent parts only contain the encoded data
                            # Find the base name of the file by removing the bucket number suffix
                            base_name = filename.rsplit('_', 1)[0] + '.txt'
                            
                            # Find the corresponding first part of the file (e.g., file_1.txt)
                            first_part_file = os.path.join(encoded_dir, base_name)
                            if os.path.isfile(first_part_file):
                                with open(first_part_file, 'r') as first_file:
                                    first_part_data = first_file.read().strip()
                                    file_name, _ = first_part_data.split(':', 1)  # Get the file name

                                    # Decode the current part of the file
                                    decoded_data = base64.b64decode(encoded_data)

                                    # Append to the existing file (reconstructing it)
                                    output_file_path = os.path.join(output_dir, f"reconstructed_{file_name}")
                                    with open(output_file_path, 'ab') as outfile:
                                        outfile.write(decoded_data)

                    print(f"Decoded {filename}")

                except Exception as e:
                    print(f"ERROR:: processing {filename}: {e}")
    
    except FileNotFoundError:
        print(f"Error: Directory '{encoded_dir}' not found.")
    except Exception as e:
        print(f"Error processing directory '{encoded_dir}': {e}")


if len(sys.argv) < 3:
    print("Provide Some Valid Options:")
    print_usage()
    sys.exit(1)

if option == "encode":
    try:
        size_of_bucket = sys.argv[4]
    except IndexError:
        size_of_bucket = 1
        print("No Bucket Size specified: Default Bucket Size = 1GB")

    # Validate the output directory path
    try:
        OUTPUT_DIR = sys.argv[3]
        if not os.path.isdir(OUTPUT_DIR):
            print("Creating the OUTPUT_DIR");
            os.makedirs(OUTPUT_DIR, exist_ok=True)
    except IndexError:
        print(f"Provide a valid directory path for <output_dir>")
        sys.exit()
    
    if not os.path.isdir(IN_DIR):
        print(f"Error: Directory '{IN_DIR}' does not exist.")
        sys.exit(1)
    
    encode_images(IN_DIR, OUTPUT_DIR, int(size_of_bucket))
    print(f"TOTAL FILES -> {number_of_files}")

elif option == "decode":
    try:
        if (sys.argv[3]):
            OUT_IMAGE_DIR = sys.argv[3]
    except IndexError:
        print(f"All the data is written into ./Output dir")

    if not os.path.isdir(IN_DIR):
        print(f"ERROR:: File '{IN_DIR}' not found.")
        sys.exit(1)
    if not os.path.isdir(OUT_IMAGE_DIR):
        os.mkdir(OUT_IMAGE_DIR)
    decode_images(IN_DIR, OUT_IMAGE_DIR)
else:
    print("Invalid option provided.")
    print_usage()
    sys.exit(1)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Program ran for: {elapsed_time:.6f} seconds")

