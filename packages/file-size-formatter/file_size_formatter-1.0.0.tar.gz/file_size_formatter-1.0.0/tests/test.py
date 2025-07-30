from file_size_formatter import format_bytes

def test_zero():
    assert format_bytes(0) == "0 Bytes"

def test_kb():
    assert format_bytes(1024) == "1.00 KB"

def test_mb():
    assert format_bytes(1832959) == "1.75 MB"

def test_precision():
    assert format_bytes(1832959, decimals=1) == "1.8 MB"
