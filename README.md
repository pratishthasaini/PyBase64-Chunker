# Base64 Image Encoder/Decoder

Python script for encoding files to Base64 format with chunking capabilities and decoding them back to their original form.

## Features
- Encode any file to Base64 format
- Split encoded data into configurable size chunks
- Decode and reconstruct original files 
- Configurable output paths
- error handling

## Requirements
- Python 3.x
- Standard libraries: os, re, sys, time, base64

## Installation
```bash
git clone https://github.com/pratishthasaini/PyBase64-Chunker
cd PyBase64-Chunker
```

## Usage
```bash
# Encoding
python main.py encode <folder_path> <output_dir> <bucket_size_gb>

# Decoding
python main.py decode <encoded_dir> <output_dir>
```

### Examples
```bash
# Encode files in 2GB chunks
python maint.py encode ./images ./encoded 2

# Decode files
python main.py decode ./encoded ./output
```

### Parameters
- `encode`:
  - `folder_path`: Source directory
  - `output_dir`: Output directory for encoded files
  - `bucket_size_gb`: Chunk size in GB (default: 1)

- `decode`:
  - `encoded_dir`: Directory with encoded files
  - `output_dir`: Directory for reconstructed files

## Output Format
- Encoded: `filename_1.txt`, `filename_2.txt`, etc.
- Decoded: Files with "reconstructed_" prefix

## Error Handling
- Directory validation
- File processing error reporting
- Automatic output directory creation
