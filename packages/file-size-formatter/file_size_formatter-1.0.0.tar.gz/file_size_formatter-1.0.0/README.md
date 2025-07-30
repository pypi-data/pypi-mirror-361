# file_size_formatter

Converts file sizes from bytes to human-readable formats like KB, MB, GB, TB with precision control.

## Usage

```python
from file_size_formatter import format_bytes

print(format_bytes(1832959))         # "1.75 MB"
print(format_bytes(1832959, 1))      # "1.8 MB"
