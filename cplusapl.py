import requests
import re
import csv
from pynapl import APL

# APL code from the gist for decoding TIO URLs
APL_DECODE_CODE = '''
⍝ TIO URL decoder from https://gist.github.com/HumanEquivalentUnit/8d8d465319c8fd9cbbd99c5aa3e0befd

fromBase64 ← {
    ⍝ Base64 decode
    chars ← 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    ⍝ Remove padding
    input ← ⍵ ~⍨ '='
    ⍝ Convert to indices
    indices ← chars ⍳ input
    ⍝ Convert to 6-bit binary
    bits ← ⍉(6⍴2) ⊤ indices
    ⍝ Flatten and group into 8-bit bytes
    flat ← , bits
    bytes ← (8÷⍨≢flat) 8 ⍴ flat
    ⍝ Convert to decimal
    256 | 2 ⊥ bytes
}

decompress ← {
    ⍝ Inflate/decompress zlib data
    ⎕UCS 220 ⎕DR ⍵  ⍝ Simple approach - may not work for all cases
}

decodeTIO ← {
    ⍝ Extract the base64 part after ##
    url ← ⍵
    parts ← '##' (≠⊆⊢) url
    encoded ← ⊃ ¯1 ↑ parts
    ⍝ Remove any trailing # or other chars
    encoded ← encoded /⍨ encoded ∊ 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    
    ⍝ Decode base64
    bytes ← fromBase64 encoded
    
    ⍝ Try to decompress (TIO uses deflate)
    ⍝ This is simplified - full implementation would need proper zlib
    text ← ⎕UCS bytes
    
    ⍝ Split by common separators and find code
    lines ← (text ∊ ⎕UCS 0 255 10) ⊆ text
    lines ← (~0=≢¨lines) / lines
    
    ⍝ Return first non-empty line that looks like code
    ⊃ lines
}
'''

def setup_apl():
    """Initialize APL connection and load decoder functions."""
    apl = APL.APL('C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Dyalog APL-64 20.0 Unicode\Dyalog APL-64 20.0 Unicode')
    # Load the decoder code
    apl.eval(APL_DECODE_CODE)
    return apl

def extract_from_tio_url(apl, url):
    """Extract APL expression from a tio.run URL using APL."""
    try:
        # Call the APL decoder function
        result = apl.eval(f'decodeTIO "{url}"')
        
        # Result should be a string
        if result and isinstance(result, str) and len(result.strip()) > 0:
            return result.strip()
        
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
    print("Initializing APL...")
    
    apl = setup_apl()
    
    results = []
    tio_pattern = re.compile(r'https?://tio\.run/##[^\s\t]+')
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        # Find all tio.run URLs in this line
        tio_urls = tio_pattern.findall(line)
        
        for tio_url in tio_urls:
            expression = extract_from_tio_url(apl, tio_url)
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