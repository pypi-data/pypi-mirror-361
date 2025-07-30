# uCommand

**uCommand** is a base class that represents a unit of work to execute.  **uCommand** can be executed in the context of **uControl** or independently in the absense of a control mechanism.  The following features are available when using **uCommand**.
- **Custom command classes.** Commands are custom classes derived from **uCommand**
- **Unit level logging.** Utilizes **uLogger** for logging.  Log messages can be combined into a main log while also differentiating log messages specific to the command
- **Flexible parameter source.** Configuration for command execution can come from configuration files or be specified directly

## uCommand Implementation

**uCommand** is a base class.  Define your own custom command by providing a subclass implementation following these guidelines.

### Derivation

Define a subclass derived from the **uCommand** superclass.

```python
from m9lib import uCommand

class MyCommand(uCommand):
    
    def __init__(self):
      super().__init__()
```

### Implement execution method

You must implement a method in your superclass with this signature:

**def imp_execute(self, in_preview):**

uCommand has a built in feature for executing in preview mode, and so *in_preview* may be used for this purpose.  This value can also be used by calling **IsPreview()**

**imp_execute()** must return one of:
- True (*success*)
- "Success" (*success*)
- An error string (*failure*)

```python
class MyCommand(uCommand):
    
    def __init__(self):
      super().__init__()

    def imp_execute(self, in_preview):
        self.LogParam("MyInput")

        p = self.GetParam("MyInput", False)
        if p is False:
            return "No input specified"

        print("do work")

        return "Success"
```

### Parameters

There is a helper method for logging parameters in a consistent way.

**LogParam(*Param*, *Value*=None)**
- Logs the specified parameter
- If *Value* is None, loads the value from parameters

Command defaults can be established by calling **SetDefaults()**.  This is helpful because it is applied at a low-level, so even when a default isn't provided, it is established by the command.  This method should be called in the command constructor after initializing the super class.

**SetDefaults(Defaults)**
- Expects a list of (*name*, *value*)
- Internally, all values are converted to *str*, then converted to the appropriate type by the access method
- Replaces any previously established defaults for this command

Access parameters using these methods.  If the parameter is not available, the *Default* value will be used.

  - **GetParam**(*Param*, *Default*=None)
  - **GetIntParam**(*Param*, *Default*=None)
  - **GetFloatParam**(*Param*, *Default*=None)
  - **GetBoolParam**(*Param*, *Default*=None)
  - **GetListParam**(*Param*, *Default*=None)

```python
# set defaults example

class comTest(uCommand):
    
    def __init__(self):
        super().__init__()
        self.SetDefaults([('my_number', 12), ('ima_bool', True), ('third_value', "3.33")])
```

### Logging parameters

**LogParam(*Param*, *Value*=None, *IfNone*=True)**
- *Param*: Parameter name
- *Value*: Value of parameter.  If *None*, read parameter value using **GetParam()**
- *IfNone*: If the parameter value is not set (or specified), and this value is *False*, returns without logging
  
**LogParams(*ParamList*, *IfNone*=True)**
- Logs a list of parameters using **LogParam()**
- *ParamList* can be a list of string or tuples where the second value is passed in as *Value*

**LogParamString(*ParamString*, *ParamStringNone*=None, *IfNone*=True)**
- Logs *ParamString* after replacing parameter values represented as `[=<param>]`.
- If any of the the param values are *None*:
  - If *IfNone* is *False*, return without logging
  - If *ParamStringNone* is not *None*, use this string instead of *ParamString*

**LogParamStrings(*ParamStringList*, *IfNone*=True)**
- Logs a list of param strings using **LogParamString()**.
- List can contain a combination of strings and tuples where the second value is passed as *ParamStringNone*.

```python
# log p1, getting the value from internal parameters; will still display if there is no p1 parameter
self.LogParam("p1")
# log p1, p2, p3 but skip logging a parameter if it is None; p2 displays as "red" instead of reading from parameters
self.LogParams(["p1", ("p2", "red"), "p3"])
# log p1 and p2 in a single string; if either is missing from parameters, display second string
self.LogParamString("Params are [=p1] and [=p2]", "One or more parameter values are missing")
# log p1, p2, and p3; if p2 is missing, display a special string
self.LogParamStrings(["p1 is [=p1]", ("p2 is [=p2]", "p2 is missing"), "p3 is set to [=p3]!"])
```

### Logging messages

**uCommand** logging methods write a log message to the main log and also maintain a copy of the messages in the command result.

- **LogDetails(*Message*)**
- **LogMessage(*Message*)**
- **LogWarning(*Message*)**
- **LogError(*Message*)**

### Command registration (for uControl)

Add a call to register your custom class to your python file.

**uCommandRegistry.RegisterCommand(*CommandClass*, *ResultClass*=None)**
- Call to register your custom command class
- The registration entry is based on the class name
- *ResultClass* can be used for specifying a custom result class.  If this is None, **uCommandResult** will be used for the result

```python
uCommandRegistry.RegisterCommand(MyCommand)
```

This is only required when using **uControl**.  This allows command objects to be created by name using **uCommandRegistry**.

```python
# returns a MyCommand object
com = uCommandRegistry.NewCommand("MyCommand")
```

## uCommand Execution

To learn about command execution using **uControl**, see [uControl documentation](control.md)

The below information applies to executing commands independent of **uControl**.

### Configuration

An optional configuration can be provided for the command.  Configuration is not required.

**SetConfig(*Config*)**
- *Config* may be a **uConfig** object
- When *Config* is a **str**, configuration will be loaded from the specified file, and can be accessed via **GetConfig()**

### Logging

An optional logging file can be provided for the command.  Logging is not required.

**SetLogger(*Logger*)**
- *Logger* may be a **uFileLogger** object
- When *Logger* is a **str**, log messages will be appended to the specified file, and can be accessed via **GetLogger()**

### Execution and targeting

To execute a command, use **Execute(*Target*=None, *Preview*=False)**

Targeting allows parameters for the command to be loaded from configuration, or specified directly.

### Loading parameters from a configuration file

When configuration is specified, parameters can be loaded from a configuration section.  This section must have a class name that matches the command class name.  When there is only one matching section, *Target* can be left as None, otherwise a section id may be specified.  When an id is specified, the section class must still match.  If there are 0 matches or multiple matches, execution fails.

```python
# config.ini
[MyCommand:myid]
MyInput=42
```

```python
com = MyCommand()
com.SetConfig("config.ini")
com.Execute("myid")
```

### Specifying parameters directly

Parameters can be provided directly via a **dict** or **uDictionary**.

Even though parameters are provided directly, a configuration file may still be useful for general settings or other purposes.

```python
com = MyCommand()
com.Execute({MyInput:42})
```

### Providing a uConfigSection

A **uConfigSection** can be specified directly.  The class name must still match.

```python
cfg = uConfig("config.ini")
section = cfg.GetSection("MyCommand","myid")

com = MyCommand()
com.Execute(section)
```

## Command Results

The **Execute()** method returns a **uCommandResult**.  In its simplest use, the return value of **imp_execute()** is stored within **uCommandResult**, and can be accessed later.
- **GetCommandId()**: Returns an id associated with the command execution.  Typically, this comes from the configuration section used for execution parameters
- **GetCommandClass()**: Returns the command class name
- **GetSpecification()**: Returns the command section header specification
- **GetResult()**: Returns the result returned from **imp_execute()**
- **IsSuccess()**: Returns True when the result returned from **imp_execute()** is "Success" or True
- **GetDuration()**: Returns total execution time in seconds
- **GetMessages(*Level*=None)**: Returns a list of messages logged to this command as [(`<level>`, `<message>`)].  If Level is specified, returns only messages >= Level.
- **CountWarnings()**: Returns the count of warning messages
- **CountErrors()**: Returns the count of error messages

### Custom command results

When using a custom command result subclass:
- Include the class in the **uCommandRegistry.RegisterCommand()** call
- Access the result object within **imp_execute()** by calling **GetResult()**

## Use example

This is an example of direct execution.

```python
from m9lib import uCommand, uCommandResult, uCommandRegistry

class MyCommandResult(uCommandResult):

    def __init__(self):
      super().__init__()

    def SetInfo(self, Info):
      self.info = Info

    def GetInfo(self):
      return self.info

class MyCommand(uCommand):
    
    def __init__(self):
      super().__init__()

    def imp_execute(self, in_preview):
        result = self.GetResult()
        self.LogParamStrings(["In this example, SetInfo() will use [=MyInput]", "Also: [=aParam]"])
        p = self.GetParam('MyInput')
        result.SetInfo(f"MyInput is {p}")
        return "Success"

uCommandRegistry.RegisterCommand(MyCommand, MyCommandResult)

com = uCommandRegistry.NewCommand("MyCommand")
com.SetLogger(uLogger(PrintLevel=uLoggerLevel.INFO, PrintColor=True))
result = com.Execute({'MyInput':42, 'aParam':"roses are red"})
if result.IsSuccess():
  print("Result: " + str(result.GetResult()))
  print("Info: " + result.GetInfo())
```
