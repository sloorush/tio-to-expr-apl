#!/usr/bin/env python3
"""Analyze why some TIO links don't yield expressions."""

import csv
import zlib
import base64
import urllib.request
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def decode_tio_link_debug(tio_url):
    """Decode with debug info."""
    if not tio_url or not tio_url.startswith('https://tio.run/##'):
        return None, "Not a TIO link"

    try:
        encoded_data = tio_url.split('##')[1]
        padding = len(encoded_data) % 4
        if padding:
            encoded_data += '=' * (4 - padding)

        compressed_data = base64.b64decode(encoded_data)
        decompressed_data = zlib.decompress(compressed_data, -zlib.MAX_WBITS)
        parts = decompressed_data.split(b'\xff')

        # Debug: show all parts
        decoded_parts = []
        for i, part in enumerate(parts):
            if part:
                try:
                    decoded_parts.append(f"Part {i}: {part.decode('utf-8', errors='ignore')[:50]}")
                except:
                    decoded_parts.append(f"Part {i}: [binary data]")

        if len(parts) > 2 and parts[2]:
            code = parts[2].decode('utf-8', errors='ignore').strip()
            if code:
                return code, "Success"
            else:
                return None, f"Part 2 is empty. Parts: {decoded_parts}"
        else:
            return None, f"Not enough parts (got {len(parts)}). Parts: {decoded_parts}"

    except Exception as e:
        return None, f"Error: {str(e)}"


# Fetch the table
url = 'https://raw.githubusercontent.com/abrudz/aplcart/refs/heads/master/table.tsv'
print("Fetching APLcart table...")
with urllib.request.urlopen(url) as response:
    content = response.read().decode('utf-8')

reader = csv.reader(content.splitlines(), delimiter='\t')
next(reader)  # Skip header

failed_links = []
for row in reader:
    if len(row) >= 8:
        syntax = row[0]
        description = row[1]
        tio_link = row[7]

        if tio_link and tio_link.startswith('https://tio.run/'):
            code, reason = decode_tio_link_debug(tio_link)
            if code is None:
                failed_links.append({
                    'syntax': syntax,
                    'description': description[:60],
                    'link': tio_link,
                    'reason': reason
                })

print(f"\nTotal failed TIO links: {len(failed_links)}\n")

# Show first 10 failures
print("First 10 failed links:")
for i, item in enumerate(failed_links[:10]):
    print(f"\n{i+1}. {item['syntax']} - {item['description']}")
    print(f"   Reason: {item['reason']}")
    print(f"   Link: {item['link'][:80]}...")
