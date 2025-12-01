# TIO-to-Expr APL

Extract APL expressions from tio.run links in the APLcart database.

## Overview

This tool downloads the [APLcart](https://aplcart.info) TSV table and extracts executable APL code from the embedded tio.run links. APLcart is a comprehensive searchable database of APL primitives and idioms.

## Quick Start

```bash
python tio_to_expr.py
```

The script will:
1. Fetch the APLcart table from GitHub
2. Extract expressions from 720+ tio.run links
3. Show you the first 10 examples
4. Offer export options (CSV, text, or both)

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)

## Output Formats

### CSV Format
- **File**: `apl_expressions.csv`
- **Columns**: `syntax`, `description`, `expression`, `tio_link`
- **Encoding**: UTF-8
- **Features**: All fields quoted to handle multi-line expressions and special characters

### Text Format
- **File**: `apl_expressions.txt`
- **Format**: Human-readable with clear separators
- **Encoding**: UTF-8

## Statistics

- **Total APLcart entries**: 3,726
- **Entries with TIO links**: 801 (21.5%)
- **Successfully extracted**: 720 (89.9% of TIO links)
- **Export ready**: All 720 expressions with proper formatting

## Example Output

```csv
"syntax","description","expression","tio_link"
"⍬","Empty Numeric Vector","⎕← ⍬ ≡ 0⍴0","https://tio.run/##..."
"⊢Y","Same (I-combinator): Y","⎕← ⊢  1 2 3","https://tio.run/##..."
```

## How It Works

TIO.run (Try It Online) links encode executable code in the URL:

1. **Extract** base64-encoded data from the URL fragment
2. **Decode** base64 (with special handling for non-standard encoding)
3. **Decompress** using zlib (raw deflate format)
4. **Parse** the decompressed data structure
5. **Extract** the APL code

## Files

- `tio_to_expr.py` - Main script
- `debug_tio.py` - Debug/test TIO link format
- `test_decode.py` - Test problematic links
- `analyze_missing.py` - Analyze failed extractions
- `apl_expressions.csv` - Generated CSV output
- `apl_expressions.txt` - Generated text output

## Technical Notes

### TIO Link Format
```
https://tio.run/##<base64_compressed_data>
```

The data is:
- Base64-encoded (with `@` sometimes used instead of `+`)
- Zlib-compressed (raw deflate)
- Structured with 0xFF separators
- Contains: language, code, input, arguments

### Windows Compatibility
The script automatically sets UTF-8 encoding on Windows to properly display APL Unicode characters.

## License

This tool is for extracting data from the public APLcart database.
APLcart is created and maintained by Adám Brudzewsky.

## Links

- [APLcart](https://aplcart.info)
- [APLcart GitHub](https://github.com/abrudz/aplcart)
- [TIO.run](https://tio.run)
- [Dyalog APL](https://www.dyalog.com)

---
---

Written with claude code
