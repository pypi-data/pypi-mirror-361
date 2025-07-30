# m9lib Utility Library

m9lib is a python framework for batch processing.  This library also includes general-purpose helper classes for python applications.

The batch processing framework includes:
- A powerful and flexible **Configuration** file format (INI) that drives batch processing
- Support for user-implemented **Command** objects that represent a unit of work to be executed
- A **Control** mechanism for instantiating and executing **Command** objects via configuration
- Integrated **Logging** features, including console logging in color
- Rules-based folder scans using pattern matching, regex, and parent folder

## m9lib Project Creator

The easiest way to get started is with a simple empty project, using the [m9lib project creator](https://github.com/MarcusNyne/m9lib-project).
- Run this application to create an empty vscode project from a template.
- The application itself is a simple example of an m9lib project.

## Sample Projects

A working demonstration of **m9lib** is available from the sample projects below:
- [m9lib-project](https://github.com/MarcusNyne/m9lib-project): Create a simple **m9lib** project from a template. (*simple*)
- [unzip-files](https://github.com/MarcusNyne/unzip-files): Batch process for unziping files. (*simple*)
- [file-sync](https://github.com/MarcusNyne/file-sync): Rules-based folder synchronization process for backing up files. (*intermediate*)

## m9ini Configuration files

**m9lib** uses **m9ini** for reading configuration files.

Read about [m9ini on Github](https://github.com/MarcusNyne/m9ini).

## Basic utilities

| File | Classes | Feature |
| :--- | :--- | :--- |
| u_logger.py | uFileLogger | [Log to a file](docs/logger.md) |
| u_format.py | uFormat | [String formatting](docs/format.md) |
| u_folder.py | uFolder | [Folder utilities](docs/folder.md) |
| u_timer.py | uTimer | [Measure elapsed time](docs/timer.md) |
| u_dictionary.py | uDictionary | [Dictionary wrapper](docs/dictionary.md) |

## Application level

| File | Classes | Feature |
| :--- | :--- | :--- |
| u_args.py | uArgs | [Specify and interpret command line parameters](docs/args.md) |
| u_command.py | uCommand, uCommandResult<br>uCommandRegistry | [Command object representing a unit of work](docs/command.md) |
| u_control.py | uControl | [Command orchestration](docs/control.md) |

## Specialized features

| File | Classes | Feature |
| :--- | :--- | :--- |
| u_csv.py | uCSVFormat, uCSV | [CSV file utilities](docs/csv.md) |
| u_web.py | uWeb, uSoap | [Http helper methods](docs/web.md) |
| u_scan.py | uScanFiles, uScanFolders | [Rules for scanning folder structures](docs/scan.md) |
| u_color.py | uColor, uConsoleColor | [Print to console in color](docs/color.md) |
