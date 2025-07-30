# uControl

**uControl** orchestrates execution of [uCommand](command.md) objects.

The entire process is driven by a configuration file ([uConfig](config.md)), from the selection of commands to the parameters passed into commands during execution.

Commands have access to shared configuration and log output.  **uControl** provides access to execution results and summaries to identify failed commands.

## High Level Summary

**1. Implement commands**

The first step is to define your commands.  Each command is a discrete unit of work defined by a python class derived from [uCommand](command.md).

uCommand provides features for accessing execution parameters, configuration, and logging.

Your custom class must be registered using **uCommandRegistry**.  The class name will be used to identify the command to execute.

**2. Create configuration file**

**uControl** is configuration-driven.  The configuration file will include global settings, including the location of the log file and a list of commands to execute, by id.

The configuration file has sections for command parameters.  Each section will have a command name, a command id, and parameters that will be passed into the command during execution.

**3. Implement control (optional)**

**uControl** can be used for command orchestration as-is.  However, by deriving your own custom class, you can extend **uControl** with custom functionality.

**4. uControl excecution**

Once everything is ready, call uControl to execute the commands listed in your configuration file.

**uControl** provides access to individual command results and a summary of the entire run.

## Getting Started

The easiest way to get started is with a simple empty project, using the [m9lib project creator](https://github.com/MarcusNyne/m9lib-project). Run this application to create an empty vscode project from a template.

*The m9lib Project Creator itself uses uCommand and uControl and so is a demonstration of these concepts.*

## uControl Setup

### Configuration file

This section provides relevant details on how to set up configuration files for **uControl**.  For more details on configuraiton file features, see [uConfig](config.md).

```ini
[MyApplication]
# uControl will use this section
Logfile = \{YMD} Output.log
Preview = False
Execute = com1,g1,AnotherCommand

[Group:g1]
# allows a group of commands to be referenced with a single id
Execute = com2,com3

[MyCommand:com1]
# MyCommand is your custom class name; com1 is the command id
p1=some input
p2=this,is,a,list

[MyCommand:com2]
p1=input value
p2=nope

[AnotherCommand:com3]
# This is a different command class
inputvalue = 1.23
notes = this is a note

[AnotherCommand]
# Note the lack of an id
inputvalue = 5.55
```

The control section has settings used by **uControl**.  The name of this section must match the *Name* passed into **uControl** constructor.
- *Logfile* (optional): Path to a log file. {YMD} will be replaced by the date. {TWM} (time since midnight) can be used to make the logfile specific to the run.  If a logfile is not specified, uses a console logger
- *Preview* (optional): A flag that is passed down to commands
- *Execute*: A list of commands to execute

*Execute* can contain any of:
- A section id where the section name corresponds to a command class
- A section id of a "Group" with an *Execute* value
- A section name where this name corresponds to a command class

In the example above, there is an overlap where "com3" is referenced both by id and by name. **uControl** will notice this and remove duplicates.

In the example above, there are four command sections. The first part of the section is the section name, followed by an optional id. In order to execute a command, the name must match a custom command class registered by **uCommandRegistry.RegisterCommand()**.

A command section can contain any number of name/value pairs.  These will be passed into the command during execution.

### Custom uControl (optional)

**uControl** can be used as-is.  However, implementing your own control allows custom code to be executed during command processing.

See details below about passing values to the **uControl** constructor.

Implement any of these **uControl** methods.

**def imp_ini_command (self, *in_command*)**
- Passes in a newly constructed uCommand (derived) object
- Perform additional initialization before the command is executed
- Return *False* to fail initialization and skip command execution

**def imp_prepare (self)**
- Called before any commands are processed; in fact, before the command list is established
- Return *False* to fail processing before any commands are executed

**def imp_finalize (self)**
- Called after commands are processed
- Command results can be accessed via **GetResults()** and **GetSummary()**
- Return a string or any value that will be accessible via **GetFinalResult()**

Utilize **GetLogger()** to log messages or change log settings
- By default, only warnings and errors are logged to the console. Use **SetPrint()** and **SetPrintLevel()** to change these settings.

## Control Execution

## Control object creation

**uControl (*Name*, *Config*, *Params*)**
- *Name*: name of a section in configuration containing control settings
- *Config*: can be a **uConfig** object, or a path to a configuration file to load
- *Params* (optional): can be a **uConfigParameters** object, or a list of [parameter specifications](config.md) when *Config* is a file to load (ignored otherwise)

If the control section in configuration has a "Logfile" setting, the logger will append to this file.  Otherwise, the logger will only write to the console.  By default, only warnings and errors are logged to the console. Use **SetPrint()** and **SetPrintLevel()** to change these settings.

A common use case for parameters is overriding configuration based on command line arguments.  For example, define all the commands and settings in configuration, but specify an execution list or output folder on the command line, then pass those arguments in as parameters.

Parameters are applied when a configuration file is loaded, which is why *Params* is ignored if the file was already loaded in the form of a **uConfig** object.

## Execute via execution list

Call **Execute(*ExeList*=None)** to begin command processing.  This method uses an execution list to build a list of commands with parameters to execute.
- If *ExeList* is *None*: execution list is loaded from configuration
- *ExeList* may be a list of commands to execute as a list or comma delimited string

*ExeList* entries can include:
- A section id where the section name corresponds to a command class
- A section id of a "Group" with an *Execute* value
- A section name where this name corresponds to a command class

The command section contains parameter values for the command, and the section class must match a command class name via **uCommandRegistry**.  In most cases, the command class is the section name, but this can be modified using a "*class" property.
```ini
[MyCommand:id1]
# class is "MyCommand"

[MyCommand:id2]
*class=SomeCommand
# class is "SomeCommand"
```

For each command selected by the execution list:
- A command object will be created using **uCommandRegistry.NewCommand()**
- **imp_ini_command()** is called to perform custom initialization (when defined)
- The command is executed by passing in the settings from the configuration section

References to command objects are released after execution to free associated memory.

## Direct command execution

Call **ExecuteCommand(*CommandName*, *CommandTarget*)** to execute a command directly.

*CommandTarget* can be one of:
- None: looks for a section by class name in configuration
- Id: looks for a section by class name and id in configuration
- dict or uDictionary: used as explicit parameters
- uConfigSection: use specified section values

When *CommandTarget* is *dict* or *uDictionary*, these values can be included:
- "*id": value is returned from GetId()
- "*name": value is returned from GetName()

If *CommandTarget* is a **uConfigSection**, *CommandName* can be None, in which case the command name is read from the config section.  The class can be specified using "*class" or defaulted to the section name.

## System Failures

System failures are queued internally to **uControl**.

An explanation of system failures are available here: [System Failures](failures.md).

**uControl.PrintFailures(*Print*=True, *PrintColor*=True)**
- Enable printing of system failures to the console
- By default, printing is off
- This enables printing for all control instances
- Automatically sets uConfig to the same settings; if you wish different settings, call *uConfig.PrintFailures()* after this call

**ClearFailures()**
- Clears the failure queue for this control

**HasFailures()**
- Returns *True* if this control has system failures

**GetFailures(*Reset*=True)**
- Returns a list of system failures
- A system failure is a tuple ({context}, {code}, {message})
- The context helps to identify if the failure happened in the control object or a specific command
- When **Reset** is *True*, the failure queue for this control is cleared

## Execution Results

**GetResults(*Name*=None, *Id*=None, *Label*=None, *IsSuccess*=None)**
- Returns a list of **uCommandResult** objects
- If all criteria is None, then all command results are returned
- One or more criteria can be specified to filter the list of results
- Only returns results for commands that actually ran; if there was a problem creating or initializing the command object, results will not be included
- *IsSuccess* is *True*, *False*, or *None* (no filtering)

**GetResult(*Id*)**
- Returns the first matching result
- *Id* can be a command id, a name, or a specification in the form *name*:*id*

**CountSuccess(*IsSuccess*=True)**
- Counts available results based on success (*True*), failure (*False*), or skipped (*None*)
- *IsSuccess* of *None* provides a count of commands that were skipped based on a problem creating or initializing the command object

**GetSkipped()**
- Returns a list of commands that were skipped (those with no results)
- A list of strings in the format `<name>:<id>`, or `<name>` when there is no id

**GetTotalErrors(*Name*=None, *Id*=None, *Label*=None)**
- Counts errors across command results
- If all criteria is None, then all command results are returned
- One or more criteria can be specified to filter the list of results

**GetFinalResult()**
- A value returned by **imp_finalize()**
- If **imp_finalize()** is not implemented, or returns None, the final result is:
  - *None*: when no commands were found to execute
  - *True*: when all commands returned "Success"
  - *False*: when one or more commands were skipped or returned a failure string

**GetDuration()**
- Returns total execution time in seconds

**GetSummary()**
- Returns a *dict* containing a summary of execution results

## Use example

Save the above configuration to **config.ini** to run this example.

```python
from m9lib import uCommand, uControl, uCommandRegistry, uLoggerLevel

class MyCommand(uCommand):
    def __init__(self):
      super().__init__()

    def imp_execute(self, in_preview):
        # print this first message in color
        self.LogMessage(f"Start command: [+VIOLET]{self.GetName()}[+]:[+CYAN]{self.GetId()}[+]")
        self.LogParam('p1')
        p2 = self.GetParam('p2')
        if p2=="nope":
          self.LogError("p2 says 'nope', so failing execution..")
          return False

        return "Success"

uCommandRegistry.RegisterCommand(MyCommand)

class MyControl(uControl):
    def __init__(self, Config, Params=None):
      super().__init__("MyApplication", Config, Params)

    def imp_ini_command (self, in_command):
      self.GetLogger().WriteLine(f"[+YELLOW]Initializing command: {in_command.GetName()}:{in_command.GetId()}[+]")
      return True

    def imp_prepare (self):
       self.GetLogger().WriteLine("[+BOLD]--- imp_prepare()[+]")

    def imp_finalize (self):
       self.GetLogger().WriteLine("[+BOLD]--- imp_finalize()[+]")
       return f"??? {self.CountTotalErrors()} total errors"

control = MyControl("config.ini")
# by default, logger only prints warnings and above, and not in color
control.GetLogger().SetPrint(True, Level=uLoggerLevel.INFO, Color=True)
# using Execute list from config, which references commands that do not exist
control.Execute()

print ("PRINT TEST RESULTS ...................")
print ("Final result is: " + control.GetFinalResult())
print (control.GetSummary())

# try execution with an execution list
control.Execute("com1")

# try execution of a specific command using uControl and the console logger
# -- this will force a failure because of p2
control = uControl("MyCommand", "config.ini")
control.GetLogger().SetPrint(True, Level=uLoggerLevel.INFO, Color=True)
control.ExecuteCommand("MyCommand", {'*id':'custom_id', 'p1':999.999, 'p2':'nope'})
```
