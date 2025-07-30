# uFileLogger

uFileLogger provides file logging capabilities.

## Instantiation

**uFileLogger(*Filepath*=None, *Print*=True, *PrintLevel*=uLoggerLevel.WARNING, *PrintColor*=False)**
- *Filepath*: filepath to create log file; if the file exists, it will be appended to
- *Print*: print log entries to console
- *PrintLevel*: only print entries greater than or equal to this level; entries must also be greater than or equal to the logging level
- *PrintColor*: use [**uConsoleColor**](color.md) for printing color to the console; Colors are stripped from file logging

```python
# start logging in constructor
logger = uFileLogger("myfile.log")

# start logging using Start() method
logger = uFileLogger()
logger.Start("myfile.log")
```

## Log Levels

Whenever lines are written to uFileLogger, messages may be filtered by log level.  The class **uLoggerLevel** enumerates the various log levels.
- *uLoggerLevel.DETAILS*: for verbose logging
- *uLoggerLevel.INFO*: the default logging level
- *uLoggerLevel.WARNING*: a warning
- *uLoggerLevel.ERROR*: an error

A log level may be set for both writting to the log and printing to the console.  The default log levels are:
- Write to log: *INFO*
- Print to console: *WARNING*

Modify logging levels by calling:
- **SetPrint(*Print*=True, *Level*=None, *Color*=None)**: Turn on/off printing; Change print level and/or Color setting
- **SetPrintLevel(*Level*)**: Set print level; Messages at lesser levels are filtered out
- **SetWriteLevel(*Level*)**: Set write level; Messages at lesser levels are filtered out

## Write Operations
A timestamp is added to all log lines.
| Method | Feature | Example |
| :--- | :--- | :--- |
| **WriteHeader(*Title*)** | A fat header | ====================<br>=== Sample Header<br>==================== |
| **WriteSubHeader(*Title*)** | A slim header | --- SubHeader ------------- |
| **WriteSubDivider(*SubheaderChar*=None, *PadAbove*=False, *PadBelow*=False, *Padding*=False)** | A divider line | -------------------------------- |
| **WriteLine()** | A line of text | Sample message |
| **WriteDetails()** | A verbose line of text | ..Sample message |
| **WriteWarning()** | A warning message | *WARN: Warning message |
| **WriteError()** | An error message | *ERROR: Error message |
| **WriteBlank()** | A blank line |  |

## Console Output

By default, log output will go to the console with a print level of uLoggerLevel.WARNING.

```python
# print log output to console in addition to file
logger = uFileLogger("myfile.log", Print=True)

# pause printing
logger.PausePrint()

# start printing
logger.SetPrint(True)
```

## Console Output (Color)

Turn on color output by setting *PrintColor* to True in the constructor or using **SetPrint()**.

This feature uses uConsoleColor colors.  If color printing is off, color syntax will be stripped out.

```python
logger = uFileLogger("myfile.log", Print=True, PrintColor=True)

# color codes will be sent to console, color codes are stripped before going to the file log
logger.WriteLine("A line of [+RED]roses[+].")

# when printcolor is off, color codes are stripped before going to the console and log
logger.SetPrint(Color=False)
logger.WriteLine("A line of [+RED]roses[+].")
```

## Counting Errors

The logger automatically maintains a count of warnings and errors.
- **GetWarningCount()**: Number of warnings
- **GetErrorCount()**: Number of errors
- **ResetCounts()**: Resets counts to 0

## Line Formatting

**ConfigFormat()** may be used to change formatting characters for header and subheader lines.

**ConfigFormat(*HeaderChar*=None, *HeaderLen*=None, *SubheaderChar*=None)**
- Specify a character, or leave as None to accept current configuration

## Extending Logging Functionality

Logging to other devices can be accomplished by deriving from uLogger.

## uLogger

**uLogger** is the base class for **uFileLogger**.  This class can be instantiated directly to enable console logging without a log file.

**uFileLogger(*Print*=True, *PrintLevel*=uLoggerLevel.WARNING, *PrintColor*=False)**

```python
import os
os.system("color")

logger = uLogger(Print=True, PrintLevel=uLoggerLevel.INFO, PrintColor=True)
logger.WriteLine("[+BLUE]Sample line[+]")
```