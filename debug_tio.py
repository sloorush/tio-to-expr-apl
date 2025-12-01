#!/usr/bin/env python3
"""Debug script to understand TIO link format."""

import gzip
import zlib
import base64

# Example TIO link from the table
tio_url = "https://tio.run/##SyzI0U2pTMzJT////1Hf1EdtExQe9a5ReNS5UMFAwTjL5P9/AA"

# Extract the base64 part
encoded_data = tio_url.split('##')[1]
print(f"Encoded data: {encoded_data}\n")

# Decode base64 (add padding if needed)
# Base64 strings should be padded to multiple of 4
padding = len(encoded_data) % 4
if padding:
    encoded_data += '=' * (4 - padding)

compressed_data = base64.b64decode(encoded_data)
print(f"Compressed data (bytes): {compressed_data}\n")

# Try zlib decompression
try:
    decompressed_data = zlib.decompress(compressed_data, -zlib.MAX_WBITS)
    print(f"Decompressed with zlib (raw deflate): {decompressed_data}\n")
except Exception as e:
    print(f"zlib failed: {e}")
    try:
        decompressed_data = gzip.decompress(compressed_data)
        print(f"Decompressed with gzip: {decompressed_data}\n")
    except Exception as e2:
        print(f"gzip also failed: {e2}")
        decompressed_data = compressed_data

# Split by 0xFF bytes (TIO format separator)
parts = decompressed_data.split(b'\xff')
print(f"Parts split by 0xFF ({len(parts)} parts):")
for i, part in enumerate(parts):
    if part:  # Skip empty parts
        try:
            decoded = part.decode('utf-8', errors='ignore')
            print(f"  Part {i}: {repr(decoded)}")
        except:
            print(f"  Part {i}: {part}")

# The code appears to be in the 3rd part (after language and first separator)
if len(parts) > 2:
    code = parts[2].decode('utf-8', errors='ignore')
    print(f"\nExtracted APL code: {code}")
