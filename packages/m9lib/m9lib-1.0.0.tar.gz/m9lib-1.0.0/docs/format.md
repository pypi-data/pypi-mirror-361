# uFormat

uFormat contains static methods for string formatting.

## Bytes
Displays bytes as a string, converting bytes to the largest possible denomination, unless a denomination is specified.

**Bytes(*Bytes*,*ByteUnits*=None)**
- Supported units: 'tb', 'gb', 'mb', 'kb', 'b'
- When *ByteUnits* is None, units are calculated automatically
  
```python
# automatically select a denomination
bytes_string = uFormat.Bytes(1234567)

# format in gigabytes
bytes_string = uFormat.Bytes(1234567, "gb")
```

## Duration
Displays a duration, converting seconds to the largest possible unit of time, unless a unit is specified.

**Duration(*Seconds*,*SecUnits*=None)**
- *Seconds* is a float value
- Supported units of time: 'h', 'm', 's'
- When *SecUnits* is *None*, units are calculated automatically
  
```python
# automatically select a denomination
duration_string = uFormat.Duration(321)

# format in minutes
duration_string = uFormat.Duration(321, "m")
```

## String
Converts a string, using substitution.  When using bytes or duration substitution, value must be passed to the method.

**uFormat.String(*String*,*Bytes*,*ByteUnits*,*Seconds*,*SecUnits*,*Now*)**
- Performs replacements and returns a string

Supported placeholders:
| Placeholder | Meaning | Parameters |
| :--- | :--- | :--- |
| {YMD} | year, month, day | *Now* (optional) |
| {LTS} | log timestamp | *Now* (optional) |
| {TSM} | seconds since midnight | *Now* (optional) |
| {B} | bytes | *Bytes*, *ByteUnits* (optional) |
| {D} | duration | *Seconds*, *SecUnits* (optional) |
| {PYF} | environment PYFOLDER |  |

## Strip
Strips white spaces from the begining and end of a string.

**uFormat.Strip(*Value*)**
- Value can be a string, or a list of strings
