#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test decoding a problematic TIO link."""

import zlib
import base64
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# The problematic link
tio_url = "https://tio.run/##SyzI0U2pTMzJT////1Hf1EdtExSMFA6tN1Yw0TNVODwdzDy03kTBiAsqa6xgqGACkjE0@P8fAA"

encoded_data = tio_url.split('##')[1]
print(f"Original: {encoded_data}")
print(f"Contains @: {'@' in encoded_data}")

# Add padding
padding = len(encoded_data) % 4
if padding:
    encoded_data += '=' * (4 - padding)

# Try replacing @ with +
encoded_data_fixed = encoded_data.replace('@', '+')
print(f"Fixed: {encoded_data_fixed}")

try:
    compressed_data = base64.b64decode(encoded_data_fixed)
    print(f"Base64 decode: SUCCESS")

    decompressed_data = zlib.decompress(compressed_data, -zlib.MAX_WBITS)
    print(f"Zlib decompress: SUCCESS")

    parts = decompressed_data.split(b'\xff')
    if len(parts) > 2:
        code = parts[2].decode('utf-8', errors='ignore').strip()
        print(f"Extracted code: {code}")
except Exception as e:
    print(f"Error: {e}")
