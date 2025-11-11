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
        except Exception as e:
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
        # Try different common separators
        separators = ['\xff', '\x00', '\n']
        
        for sep in separators:
            if sep in text:
                sections = text.split(sep)
                # Look for APL code (contains APL symbols)
                apl_pattern = re.compile(r'[⍝⍺⍵⌈⌊⍴⌹←→↑↓∇∆⍎⍕⊂⊃∪∩⊥⊤∈⍳⍸≤≥≠∧∨⍱⍲⌿⍀¨⍨⊆⊇○⌽⍉⊖⍟⍱⍲⌷≡≢⊢⊣⍤⍥⍠⍞⍬⎕]')
                
                for section in sections:
                    section = section.strip()
                    if section and len(section) > 2:
                        # Check if it looks like APL code
                        if apl_pattern.search(section):
                            # Get first line if multi-line
                            lines = section.split('\n')
                            for line in lines:
                                line = line.strip()
                                if line and not line.startswith('Vlang'):
                                    return line
        
        # Fallback: return first substantial non-empty section
        for sep in separators:
            if sep in text:
                sections = text.split(sep)
                for section in sections:
                    section = section.strip()
                    if len(section) > 5 and not section.startswith('apl-'):
                        lines = section.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line:
                                return line
                
        return None
    except Exception as e:
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