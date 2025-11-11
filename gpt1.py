import re
import base64
import zlib
import urllib.request

url = "https://raw.githubusercontent.com/abrudz/aplcart/refs/heads/master/table.tsv"

print("Downloading APLcart table...")
with urllib.request.urlopen(url) as response:
    data = response.read().decode("utf-8")

# Find all tio.run links
links = re.findall(r'https://tio.run/##[^\s\t]+', data)
print(f"Found {len(links)} TIO links")

expressions = []

for link in links:
    encoded = link.split("##", 1)[1]

    # TIO uses urlsafe base64 but replaces '/' with '@'
    encoded = encoded.replace("@", "/")

    # Re-pad for Base64
    encoded += "=" * (-len(encoded) % 4)

    try:
        # Decode base64 then decompress using raw DEFLATE (-15)
        decoded = zlib.decompress(base64.urlsafe_b64decode(encoded), -15).decode("utf-8", "ignore")

        # Extract the part after 'F' (the expression)
        if "\nF\n" in decoded:
            expr = decoded.split("\nF\n", 1)[1].strip()
        elif "F" in decoded:
            expr = decoded.split("F", 1)[1].strip()
        else:
            expr = decoded.strip()

        if expr:
            expressions.append(expr)

    except Exception as e:
        print(f"Error decoding {link[:80]}...: {e}")

# Remove duplicates and empty entries
expressions = [e for e in dict.fromkeys(expressions) if e.strip()]

# Save to file
with open("apl_expressions.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(expressions))

print(f"\n✅ Decoded {len(expressions)} expressions. Saved to apl_expressions.txt.")
