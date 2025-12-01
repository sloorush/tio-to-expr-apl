# TIO-TO-EXPR-APL PROJECT LOG

## Project Purpose

Extract APL expressions from tio.run links in the APLcart TSV table.
APLcart is a comprehensive searchable database of APL primitives and idioms.

## Source Data

- **URL**: https://raw.githubusercontent.com/abrudz/aplcart/refs/heads/master/table.tsv
- **Format**: Tab-separated values (TSV) with 9 columns
- **Total Entries**: 3,726 rows

### Column Structure

1. **SYNTAX** - The APL symbol or expression
2. **DESCRIPTION** - What the symbol/function does
3. **CLASS** - Primitive or System
4. **TYPE** - Function type (Monadic, Dyadic, etc.)
5. **GROUP** - Operator classification
6. **CATEGORY** - Functional category
7. **KEYWORDS** - Search terms and aliases
8. **TIO** - Link to Try It Online execution (column index 7)
9. **DOCS** - Link to official Dyalog documentation

## Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| Total APLcart entries | 3,726 | 100% |
| Entries with TIO links | 801 | 21.5% |
| Successfully extracted | 720 | 19.3% of total, 89.9% of TIO links |
| Failed to decode | 81 | 10.1% of TIO links |
| No TIO links | 2,925 | 78.5% |

## Technical Details - TIO Link Format

TIO.run links encode executable code in the URL fragment.

**Format**: `https://tio.run/##<base64_encoded_compressed_data>`

### Decoding Process

1. **Extract** base64 data after `##` delimiter
2. **Add padding** if needed (base64 strings must be multiple of 4 characters)
3. **Handle non-standard base64 encoding**:
   - Some links use `@` instead of `+`
   - Some links use `$` instead of `/`
   - Try standard `base64.b64decode` first
   - Fall back to replacing `@` → `+` and `$` → `/` if needed
4. **Decompress** using zlib with raw deflate format (`zlib.decompress` with `-zlib.MAX_WBITS`)
5. **Split** decompressed data by `0xFF` separator bytes
6. **Extract** APL code from part 2 (after language name and separator)

### Data Structure After Decompression

```
Part 0: Language name (e.g., "apl-dyalog")
Part 1: Empty (separator)
Part 2: APL code/expression ← THIS IS WHAT WE WANT
Part 3+: Additional metadata (input, args, etc.)
```

## Key Implementation Fixes

1. ❌ **Initial implementation used gzip** - WRONG! Must use zlib raw deflate
2. ✅ **Base64 padding required** - many links don't have proper padding
3. ✅ **Non-standard base64** - `@` character used instead of `+` in many links
4. ✅ **CSV export needs QUOTE_ALL** - to handle multi-line expressions and quotes
5. ✅ **Windows console requires UTF-8 encoding** - wrapper for APL characters

## Files in Project

| File | Purpose |
|------|---------|
| `tio_to_expr.py` | Main script to extract and export expressions |
| `debug_tio.py` | Debug script to understand TIO link format |
| `test_decode.py` | Test script for problematic links |
| `analyze_missing.py` | Script to analyze why some TIO links fail |
| `apl_expressions.csv` | Output CSV with 720 expressions (properly quoted) |
| `apl_expressions.txt` | Output text format |
| `README.md` | User documentation |

## Output Format (CSV)

- **Columns**: `syntax`, `description`, `expression`, `tio_link`
- **Encoding**: UTF-8
- **Quoting**: `csv.QUOTE_ALL` (all fields quoted to handle newlines and special chars)

## Known Issues

- ⚠️ **81 TIO links still fail to decode** (10.1%)
  - Most likely empty or malformed links
- ℹ️ **2,925 entries have no TIO links** at all (only documentation links)

## Future Improvements

- [ ] Investigate why 81 TIO links fail
- [ ] Add JSON export option
- [ ] Add filtering by category/keywords
- [ ] Batch processing mode without interactive prompts
- [ ] Better error reporting for failed links
- [ ] Option to include entries without TIO links (using docs links instead)

## Implementation Code Reference

### Decoding Function (Core Logic)

```python
def decode_tio_link(tio_url):
    # Extract base64 part
    encoded_data = tio_url.split('##')[1]

    # Add padding
    padding = len(encoded_data) % 4
    if padding:
        encoded_data += '=' * (4 - padding)

    # Decode base64 (handle @ and $ characters)
    try:
        compressed_data = base64.b64decode(encoded_data)
    except:
        encoded_data_fixed = encoded_data.replace('@', '+').replace('$', '/')
        compressed_data = base64.b64decode(encoded_data_fixed)

    # Decompress with zlib
    decompressed_data = zlib.decompress(compressed_data, -zlib.MAX_WBITS)

    # Extract code from part 2
    parts = decompressed_data.split(b'\xff')
    if len(parts) > 2 and parts[2]:
        code = parts[2].decode('utf-8', errors='ignore').strip()
        return code
```

## Links & Resources

- [APLcart](https://aplcart.info) - The APL primitives and idioms database
- [APLcart GitHub](https://github.com/abrudz/aplcart) - Source repository
- [TIO.run](https://tio.run) - Try It Online
- [Dyalog APL](https://www.dyalog.com) - APL implementation
