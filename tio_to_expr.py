#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract APL expressions from tio.run links in the APLcart TSV table.
"""

import csv
import zlib
import base64
import urllib.request
import sys
import os

# Set UTF-8 encoding for console output (Windows compatibility)
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def decode_tio_link(tio_url):
    """
    Decode a tio.run URL to extract the code/expression.

    TIO.run links encode the code as base64-encoded zlib-compressed data.
    Format: https://tio.run/##<base64_encoded_compressed_data>

    The decompressed format uses 0xFF bytes as separators:
    [language_name, 0xFF, 0xFF, code, 0xFF, ...]
    """
    if not tio_url or not tio_url.startswith('https://tio.run/##'):
        return None

    try:
        # Extract the base64 part after ##
        encoded_data = tio_url.split('##')[1]

        # Add padding if needed (base64 requires length to be multiple of 4)
        padding = len(encoded_data) % 4
        if padding:
            encoded_data += '=' * (4 - padding)

        # Decode base64 (try both standard and URL-safe variants)
        # Some TIO links use @ and $ instead of + and /
        try:
            compressed_data = base64.b64decode(encoded_data)
        except:
            # Try URL-safe base64
            try:
                compressed_data = base64.urlsafe_b64decode(encoded_data)
            except:
                # Try replacing @ and $ with + and /
                encoded_data_fixed = encoded_data.replace('@', '+').replace('$', '/')
                compressed_data = base64.b64decode(encoded_data_fixed)

        # Decompress using zlib (raw deflate format)
        decompressed_data = zlib.decompress(compressed_data, -zlib.MAX_WBITS)

        # Split by 0xFF separator bytes
        parts = decompressed_data.split(b'\xff')

        # The APL code is typically in part 2 (after language name and separator)
        if len(parts) > 2 and parts[2]:
            code = parts[2].decode('utf-8', errors='ignore').strip()
            if code:
                return code

        return None
    except Exception as e:
        # Silently skip failed decodings (some links might be malformed)
        return None


def fetch_and_parse_tsv():
    """Fetch the APLcart TSV and extract expressions from TIO links."""
    url = 'https://raw.githubusercontent.com/abrudz/aplcart/refs/heads/master/table.tsv'

    print("Fetching APLcart table...")
    with urllib.request.urlopen(url) as response:
        content = response.read().decode('utf-8')

    # Parse TSV
    reader = csv.reader(content.splitlines(), delimiter='\t')
    next(reader)  # Skip header row

    results = []
    total_rows = 0
    tio_links_found = 0
    expressions_extracted = 0

    for row in reader:
        total_rows += 1
        if len(row) >= 8:  # Ensure we have enough columns
            syntax = row[0]
            description = row[1]
            tio_link = row[7]

            if tio_link and tio_link.startswith('https://tio.run/'):
                tio_links_found += 1
                expression = decode_tio_link(tio_link)

                if expression:
                    expressions_extracted += 1
                    results.append({
                        'syntax': syntax,
                        'description': description,
                        'tio_link': tio_link,
                        'expression': expression
                    })

    print(f"\nStats:")
    print(f"  Total rows: {total_rows}")
    print(f"  TIO links found: {tio_links_found}")
    print(f"  Expressions extracted: {expressions_extracted}")

    return results


def save_to_csv(results, filename='apl_expressions.csv'):
    """Save results to CSV file."""
    os.makedirs('out', exist_ok=True)
    filepath = os.path.join('out', filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['syntax', 'description', 'expression', 'tio_link'],
                                quoting=csv.QUOTE_ALL)  # Quote all fields to handle newlines and special chars
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved {len(results)} expressions to {filepath}")


def save_to_txt(results, filename='apl_expressions.txt'):
    """Save results to text file."""
    os.makedirs('out', exist_ok=True)
    filepath = os.path.join('out', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in results:
            f.write(f"Syntax: {item['syntax']}\n")
            f.write(f"Description: {item['description']}\n")
            f.write(f"Expression: {item['expression']}\n")
            f.write(f"Link: {item['tio_link']}\n")
            f.write("-" * 80 + "\n")
    print(f"Saved {len(results)} expressions to {filepath}")


def save_expressions_only(results, filename='expressions_only.txt'):
    """Save only the raw APL expressions (one per line)."""
    os.makedirs('out', exist_ok=True)
    filepath = os.path.join('out', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in results:
            f.write(f"{item['expression']}\n")
    print(f"Saved {len(results)} expressions to {filepath}")


def main():
    results = fetch_and_parse_tsv()

    print(f"\n=== Sample Expressions ===")
    for i, item in enumerate(results[:10]):  # Show first 10
        print(f"\n{i+1}. {item['syntax']} - {item['description']}")
        print(f"   Expression: {item['expression']}")
        print(f"   Link: {item['tio_link']}")

    # Optionally save to file
    print("\nExport options:")
    print("  1. CSV format")
    print("  2. Text format")
    print("  3. Expressions only (one per line)")
    print("  4. All formats")
    print("  5. Skip")
    choice = input("Choose option (1-5): ").strip()

    if choice == '1':
        save_to_csv(results)
    elif choice == '2':
        save_to_txt(results)
    elif choice == '3':
        save_expressions_only(results)
    elif choice == '4':
        save_to_csv(results)
        save_to_txt(results)
        save_expressions_only(results)
    else:
        print("Skipping save.")


if __name__ == '__main__':
    main()
