# uColor

Color utilities.

## Print to the console in color

### Supported colors

The following color codes are supported:
- _END_: return to default formatting
- Decorations: _BOLD_, _ITALIC_, _UNDERLINE_
- Base colors: _RED_, _GREEN_, _YELLOW_, _BLUE_, _VIOLET_, _CYAN_, _WHITE_, _GREY_
- Light colors: *LT_RED*, *LT_GREEN*, *LT_YELLOW*, *LT_BLUE*, *LT_VIOLET*, *LT_CYAN*, *BRIGHTWHITE*
- Background colors: *BG_RED*, *BG_GREEN*, *BG_YELLOW*, *BG_BLUE*, *BG_VIOLET*, *BG_VIOLET*

The color names in this class are tuned to Windows system colors.  Different systems may display colors that are different than those described.

If your console is not providing support for Ascii color codes, try the following.
```python
import os
os.system("color")

from m9lib import uConsoleColor
print(uConsoleColor.Format("[+BG_GREEN]Simple[+] [+BOLD][+VIOLET]color[+] [+BG_RED]test[+]."))
```

You can test your console colors by calling the class method **uConsoleColor.PrintTest()**.

### Color string formatting

Use **uConsoleColor** class methods when formating strings for printing.

**uConsoleColor.Wrap(*String*, *Color*)**
- Wraps String in Ascii color codes

**uConsoleColor.Format(*String*, *StripColors*=False)**
- Perform string replacements on String where `[+COLOR]` is replaced by Ascii color codes
- `[+]` is equivalent to `[+END]`
- If *StripColors* is True, all color formatting will be removed

```python
from m9lib import uConsoleColor

# the following lines are equivalent
print(uConsoleColor.Wrap("Roses", "RED"))
print(uConsoleColor.Format("[+RED]Roses[+]"))

# remove all color formatting
print(uConsoleColor.Format("These [+RED]Roses[+] have no color", StripColors=True))

# of course, Format() is more flexible
print(uConsoleColor.Format("Roses are [+RED]red[+]; Violets are [+BLUE]blue[+]."))
```

### Simple print utility

The **uConsoleColor** class provides a simple utility for printing in color by instantiating an object with an optional system name.

**uConsoleColor(*System*=None)**
- If System is provided, the system name will be prefixed to all output

**Header(*String*=None)**
- Prints a colorful header line with an optional string

**Message(*String*)**
- Print a message to the console
- The String will undergo formatting using **uConsoleColor.Format()**

**Warning(*String*)**
- Prints a warning message
- Message will print in *LT_RED* color, but otherwise is not formatted

```python
from m9lib import uConsoleColor

# use uConsoleColor for simple console logging
cc = uConsoleColor("Test")
cc.Header("This header goes to the console")
cc.Message("This is a [+BOLD][+GREEN]uConsoleColor[+] test!")
cc.Warning("Sample warning message")
```

## Color Operations

Instantiate by providing red/green/blue values.

**uColor(*red*, *green*, *blue*)**
  
### Calculate difference

Static method that calculates the difference between two color values.

**uColor.CalcDifference(*color1*, *color2*, *percent*)**
- Returns a **uColor** object that is a mid-point between *color1* and *color2* based on percentage
- Precentage is a float between 0 and 1
- *percentage* of 0 selects *color1*
- *percentage* of 1.0 selects *color2*

### Calculate gradient

Static method that produces a gradient of colors between two colors.

**uColor.CalcGradient(*color1*, *color2*, *steps*)**
- Returns a list of **uColor** objects with length of *steps*
- [0] will be *color1*
- [*steps*-1] will be *color2*
