# System Failures

Errors during execution are stored to a failure queue, and may be accessed programmatically.
- **GetFailures()**

- [uControl errors](failures.md#ucontrol-errors)
- [uCommand errors](failures.md#ucommand-errors)

## uControl errors

### [C01] No control configuration
- There was an attempt to execute uControl without configuration
- Configuration file not found or not specified
- Control section not found in configuration file

### [C02] Failed preparation step
- Custom control implementation returned a failure during imp_prepare ()

### [C03] No command sections found by name
- This failure occurs while processing an execution list.  An execution list is expected to include section names, section ids, or group ids
- A named command was found in the command registry, but no command sections were found in configuration of this name

### [C04] No command sections found by id
- This failure occurs while processing an execution list.  An execution list is expected to include section names, section ids, or group ids
- No command sections were found in configuration with the specified id

### [C05] No group execute list specified for section
- This failure occurs while processing an execution list.  An execution list is expected to include section names, section ids, or group ids
- A [Group] section was found with the specified id, but the group did not contain an "Execute" property

### [C07] Unknown command
- The class of the command section is not a registered command

### [C08] Unable to build command class
- There was a problem instantiating the registered command class

### [C09] Failed command initialization
- The custom initialization method imp_ini_command () returned a failure

### [C10] No commands specified in Execute
- The command list comes from the Execute property of the control section
- The command list is empty or not specified

## uCommand errors

### [C21] Command execution failed: section not found
- Specified command section not found in configuration

### [C22] Command execution failed: multiple matching sections
- Multiple command sections match in configuration
- There must be exactly one command section per execution

### [C23] Command execution failed: command class mismatch
- The class of the command object does not match the class of the command section

### [C88] {Custom message}
- An ERROR occured during command processing
- A custom message was provided by the command implementation
