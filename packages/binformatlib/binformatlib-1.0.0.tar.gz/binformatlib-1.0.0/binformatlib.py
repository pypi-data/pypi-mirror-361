def _to_bytes(value):
    if isinstance(value, str):
        return value.encode('utf-8')
    elif isinstance(value, int):
        return value.to_bytes((value.bit_length() + 7) // 8 or 1, 'big')
    elif isinstance(value, bytes):
        return value
    elif value is None:
        return b''
    else:
        raise TypeError(f"Unsupported type: {type(value)}")

def _flatten_fields(d, prefix=''):
    fields = []
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            fields.extend(_flatten_fields(v, key))
        else:
            fields.append((key, _to_bytes(v)))
    return fields

def tohex(value) -> str:
    return str(value).encode('utf-8').hex()

def fromhex(hex_string: bytes):
    return bytes.fromhex((hex_string).decode('utf-8'))

def pack(format: dict, output_file: str, data: bytes) -> bool:
    try:
        fmt = dict(format)  # copy to avoid mutation
        fmt["headers"]["data"] = data
        fields = _flatten_fields(fmt)

        raw = bytearray()
        for key, val in fields:
            raw += key.encode('utf-8') + b'=' + val.hex().encode('utf-8') + b'\n'
        raw += fmt["headers"]["end of file"].encode('utf-8')

        # Hex-encode entire result
        with open(output_file, 'wb') as f:
            f.write(raw.hex().encode('utf-8'))

        return True
    except Exception as e:
        print(f"[pack] Error: {e}")
        return False

def unpack(format: dict, input_file: str):
    try:
        with open(input_file, "rb") as f:
            hex_data = f.read()

        # Decode the hex-wrapped file back to raw bytes
        raw = bytes.fromhex(hex_data.decode('utf-8'))

        eof_marker = format["headers"]["end of file"].encode('utf-8')
        if eof_marker not in raw:
            print("[unpack] EOF marker not found")
            return False

        lines = raw.split(b'\n')
        result = {}
        for line in lines:
            if line.strip() == eof_marker:
                break
            if b'=' in line:
                key, hexval = line.split(b'=', 1)
                result[key.decode()] = bytes.fromhex(hexval.decode())

        return result.get('headers.data')
    except Exception as e:
        print(f"[unpack] Error: {e}")
        return False

def tohex(value):
    return str(value).encode('utf-8').hex()