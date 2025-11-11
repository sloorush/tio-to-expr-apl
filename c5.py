import requests
import re
import base64
import csv
import zlib

def fix_base64_padding(s):
    """Fix base64 padding issues."""
    # Remove any trailing characters that aren't base64
    s = re.sub(r'[^A-Za-z0-9+/=]', '', s)
    # Add padding if needed
    missing_padding = len(s) % 4
    if missing_padding:
        s += '=' * (4 - missing_padding)
    return s

def is_valid_apl_code(text):
    """Check if text looks like valid APL code."""
    # Must contain APL symbols
    apl_symbols = r'[⍝⍺⍵⌈⌊⍴⌹←→↑↓∇∆⍎⍕⊂⊃∪∩⊥⊤∈⍳⍸≤≥≠∧∨⍱⍲⌿⍀¨⍨⊆⊇○⌽⍉⊖⍟⍱⍲⌷≡≢⊢⊣⍤⍥⍠⍞⍬⎕]'
    if not re.search(apl_symbols, text):
        return False
    
    # Should not have too many non-printable characters
    printable_chars = sum(1 for c in text if c.isprintable() or c in '\n\r\t')
    if len(text) > 0 and printable_chars / len(text) < 0.8:
        return False
    
    # Should not have random binary garbage patterns
    # Check for excessive non-ASCII printable characters that aren't APL
    non_apl_weird = sum(1 for c in text if ord(c) > 127 and c not in '⍝⍺⍵⌈⌊⍴⌹←→↑↓∇∆⍎⍕⊂⊃∪∩⊥⊤∈⍳⍸≤≥≠∧∨⍱⍲⌿⍀¨⍨⊆⊇○⌽⍉⊖⍟⍱⍲⌷≡≢⊢⊣⍤⍥⍠⍞⍬⎕÷×≢¯')
    if len(text) > 0 and non_apl_weird / len(text) > 0.3:
        return False
    
    # Check for repetitive patterns (like "←Fy" repeated many times)
    # If we see the same 2-4 character sequence repeated more than 5 times, it's likely garbage
    for length in range(2, 5):
        if len(text) >= length * 5:
            for i in range(len(text) - length * 5):
                pattern = text[i:i+length]
                count = text.count(pattern)
                if count > 5 and len(pattern.strip()) > 0:
                    # Check if this pattern makes up more than 50% of the text
                    if count * length > len(text) * 0.5:
                        return False
    
    # Should have some variety in characters (not just repeating the same few)
    unique_chars = len(set(text.replace(' ', '').replace('\n', '')))
    total_chars = len(text.replace(' ', '').replace('\n', ''))
    if total_chars > 10 and unique_chars < total_chars * 0.2:
        return False
    
    return True

def extract_from_tio_url(url):
    """Extract APL expression from a tio.run URL."""
    try:
        # TIO.run URLs encode the program after ##
        match = re.search(r'##(.+?)(?:#|$)', url)
        if not match:
            return None
        
        encoded = match.group(1)
        
        # Fix padding issues
        encoded = fix_base64_padding(encoded)
        
        # Decode base64
        try:
            decoded_bytes = base64.b64decode(encoded)
        except Exception:
            return None
        
        # TIO.run uses deflate compression
        try:
            decompressed = zlib.decompress(decoded_bytes, -zlib.MAX_WBITS)
        except:
            # If decompression fails, use raw bytes
            decompressed = decoded_bytes
        
        # Convert to string
        text = decompressed.decode('utf-8', errors='ignore')
        
        # TIO format uses various byte separators
        separators = ['\xff', '\x00', '\n']
        
        candidates = []
        
        for sep in separators:
            if sep in text:
                sections = text.split(sep)
                
                for section in sections:
                    section = section.strip()
                    if not section or len(section) < 3:
                        continue
                    
                    # Skip language identifiers
                    if section.startswith('Vlang') or section.startswith('apl-'):
                        continue
                    
                    # Get first line if multi-line
                    lines = section.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and is_valid_apl_code(line):
                            candidates.append(line)
        
        # Return the first valid candidate
        if candidates:
            return candidates[0]
        
        return None
    except Exception:
        return None

def fetch_and_extract():
    """Fetch the TSV file and extract all expressions from tio.run links."""
    url = 'https://raw.githubusercontent.com/abrudz/aplcart/refs/heads/master/table.tsv'
    
    print("Fetching TSV file...")
    response = requests.get(url)
    response.raise_for_status()
    
    text = response.text
    lines = text.split('\n')
    
    print(f"Processing {len(lines)} lines...")
    
    results = []
    tio_pattern = re.compile(r'https?://tio\.run/##[^\s\t]+')
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        # Find all tio.run URLs in this line
        tio_urls = tio_pattern.findall(line)
        
        for tio_url in tio_urls:
            expression = extract_from_tio_url(tio_url)
            if expression:
                results.append({
                    'line': i,
                    'url': tio_url,
                    'expression': expression
                })
        
        if i % 100 == 0:
            print(f"Processed {i}/{len(lines)} lines...")
    
    print(f"\nComplete! Found {len(results)} expressions from tio.run links.")
    return results

def save_to_csv(results, filename='tio_expressions.csv'):
    """Save results to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['line', 'expression', 'url'])
        writer.writeheader()
        writer.writerows(results)
    print(f"Results saved to {filename}")

def main():
    results = fetch_and_extract()
    
    # Display first 10 results
    print("\nFirst 10 expressions:")
    print("-" * 80)
    for i, result in enumerate(results[:10], 1):
        print(f"{i}. Line {result['line']}: {result['expression']}")
    
    if len(results) > 10:
        print(f"\n... and {len(results) - 10} more")
    
    # Save to CSV
    save_to_csv(results)
    
    return results

if __name__ == '__main__':
    results = main()