# uArgs

Parse command line arguments.

## Argument format

This class recognizes command line arguments as options or parameters.

An option is prefixed by a dash or double-dash, may include an optional value.  If no value is specified, then the option is either on (True) or off (False).

Any argument that is not an option is considered a parameter.

Options and parameters can be specified in any order.

For example: p1 -o1 v1 p2
  - p1 is a parameter
  - o1 is an option
  - if o1 was configured to expect a value, then the value of o1 is v1
  - if o1 was not configured to expect a value, then the value of o1 is True, and v1 is treated as a parameter
  - p2 is a parameter

Option values can also be specified using a colon.  For example: p1 -o1:v1 p2

## Argument configuration

Arguments can be configured using **AddOption()** and **AddParam()**, and/or the constructor during initialization.

**AddOption(*Option*, *Short*=None, *HasValue*=False)**
- *Option*: option name
- *Short*: optional short version of the option name
- *HasValue*: when True, the option expects an additional value

**AddParam(*Param*)**
- *Param*: parameter name

**uArgs(*Options*=None, *Params*=None)**
- *Options*: a list of tuples (Option, Short, HasValue)
- *Params*: a list of parameter names
  
```python
from m9lib import uArgs

# configure arguments
args = uArgs()
args.AddOption("option1")
args.AddOption("option2", "o2")
args.AddOption("option3", "o3", True)
args.AddParam("p1")
args.AddParam("p2")

# this is equivalent
args = uArgs(["option1", ("option2", "o2"), ("option3", "o3", True)], ["p1", "p2"])
```

## Parsing arguments

After configuring the uArgs object, parse arguments using **Parse(*Args*=None)**.
- *Args* may be a list of strings
- *Args* may be a string, in which case it will be parsed.  Arguments are expected to be separated by spaces, but if an argument is wrapped in double-quotes, it may contain a space
- When *Args* is None, the system arguments will be parsed.  In this case, the first entry will be ignored

When parsing system arguments, calling Parse() is not technically necessary, since this will be called automatically when accessing arguments via **GetOption()**, **GetParam()**, etc.

If an option was expecting a value, but no value was provided, the option will not be included in parsed results, but can be found in **GetMissingOptions()**.

## Access results

After arguments are parsed, use the following methods to access results.

**HasOption(*Option*)**
- *Option* is the long name of the option
- *Option* may match the short or long name
- Returns *True* if the option was specified
- If the value is not recognized, returns False
- If the option expects a value and a value was not specified, returns False

**GetOption(*Option*)**
- If the option expects a value and a value was specified, returns the option value
- If no value is expected, returns True if the option was specified
- If no value is expected and the option is modified with :false, then returns False
- If the value is not recognized, returns False

**HasParam(*Param*)**
- Parameters are matched based on the order they are specified
- Returns True if a parameter was specified, otherwise returns False

**GetParam(*Param*)**
- Gets a parameter when specified
- Returns None if not specified
- If the parameter is not recognized, returns False

## Bad arguments

If arguments are specified that do not map to configuration, they are collected by these methods.

**GetBadOptions()** returns a list of option names that were specified, but were not recognized.

**GetBadParams()** returns a list of paramaeters that were specified, but exceeded the number of configured parameters.

If an option is configured to have avalue, but is specified without a value, it will be ignored and collected by this method.

**GetMissingOptions()**: returns a list of option names that were configured to expect values, but where no value was provided.

## Use example

```python
from m9lib import uArgs

# configure arguments
args = uArgs()
args.AddOption("option1")
args.AddOption("option2", "o2")
args.AddOption("option3", "o3", True)
args.AddOption("option5", "o5", True)
args.AddParam("p1")
args.AddParam("p2")

# parse arguments
args.Parse('-o2 -o3 sugar happy "bright sunshine" clover -o4 -o5')

# check options
o1 = args.GetOption("option1") # returns False; is a switch that was not provided
o2 = args.GetOption("option2") # returns True; is a switch that was provided
o3 = args.GetOption("option3") # returns "sugar"; sugar is the option value
print(f"bad options: {args.GetBadOptions()}") # ["o4"] was not configured
print(f"bad options: {args.GetMissingOptions()}") # ["option5"] is  expecting an option value

# check parameters
p1 = args.GetParam("p1") # returns "happy"
p2 = args.GetParam("p2") # returns "bright sunshine"
p3 = args.GetParam("p3") # returns False; was not provided
print(f"bad parameters: {args.GetBadParams()}") # ["clover"] was not configured
```
