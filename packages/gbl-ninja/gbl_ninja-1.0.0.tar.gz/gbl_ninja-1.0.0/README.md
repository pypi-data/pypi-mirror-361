# GBL Python Library

This is a Python library for parsing and creating GBL files.

## Features

*   **Parse GBL files:** Read and parse GBL files into a list of tag objects.
*   **Create GBL files:** Programmatically create GBL files using a builder pattern.
*   **Encode GBL files:** Encode a list of tag objects into a byte array.

## Usage

### Parsing a GBL File

```python
from gbl import Gbl, ParseResultSuccess, ParseResultFatal

gbl = Gbl()

with open('firmware.gbl', 'rb') as f:
    data = f.read()

result = gbl.parse_byte_array(data)

if isinstance(result, ParseResultSuccess):
    tags = result.result_list
    for tag in tags:
        print(f'Found tag: {tag.tag_type.name}')
elif isinstance(result, ParseResultFatal):
    print(f'Error parsing GBL file: {result.error}')
```

### Creating a GBL File

```python
from gbl import Gbl

builder = Gbl.GblBuilder.create()
builder.application()
builder.prog(0x1000, b'\x01\x02\x03')

gbl_bytes = builder.build_to_byte_array()

with open('new_firmware.gbl', 'wb') as f:
    f.write(gbl_bytes)
```
