import requests
import re
import base64
import csv
from urllib.parse import unquote

def extract_from_tio_url(url):
    """Extract APL expression from a tio.run URL."""
    try:
        # TIO.run URLs encode the program after ##
        match = re.search(r'##(.+?)(?:#|$)', url)
        if not match:
            return None
        
        encoded = match.group(1)
        
        # Decode base64
        decoded = base64.b64decode(encoded).decode('utf-8', errors='ignore')
        
        # TIO uses a binary format with sections separated by null bytes
        sections = decoded.split('\x00')
        
        # Look for the section containing APL code
        apl_pattern = re.compile(r'[⍝⍺⍵⌈⌊⍴⌹←→↑↓∇∆⍎⍕⊂⊃∪∩⊥⊤∈⍳⍸≤≥≠∧∨⍱⍲]')
        
        for section in sections:
            section = section.strip()
            if section and apl_pattern.search(section):
                return section
        
        # If no APL-specific characters found, return first non-empty section
        for section in sections:
            section = section.strip()
            if section:
                return section
                
        return None
    except Exception as e:
        print(f"Error decoding URL {url}: {e}")
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
        print(f"{i}. Line {result['line']}: {result['expression'][:60]}...")
    
    if len(results) > 10:
        print(f"\n... and {len(results) - 10} more")
    
    # Save to CSV
    save_to_csv(results)
    
    return results

if __name__ == '__main__':
    results = main()