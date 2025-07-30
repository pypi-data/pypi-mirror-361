# uScan

**uScan** is a tool to evaluate folder structures and file names and return a list of files/folders based on filtering rules.

This system is most helpful when developing batch processes for file maintenance where rules are specified based on file names, folder names, and file sizes.

## Filtering

A scan filter is a rule that is tested against a filepath.  A filter includes a filter type (Condition) and Details (match rules).

### Filter conditions

- pattern: file match patterns; For example: "*.txt"
- regular expression: string-based regular expression
- size: file size as bytes (int) or a string, which may include kb, mb, gb; For example: 12000, "12000", "12kb"

| Condition | Details | Explanation |
| :--- | :--- | :--- |
| PATTERN | pattern | Matches specified pattern or patterns ; delimited |
| REGEX | regular expression | Matches regular expression |
| P_PATTERN | pattern | Parent folder matches specified pattern or patterns ; delimited |
| P_REGEX | regular expression | Parent folder matches regular expression |
| PN_PATTERN | pattern | Parent folder does not match specified pattern or patterns ; delimited |
| PN_REGEX | regular expression | Parent folder does not match regular expression |
| GTSIZE | size | File size is greater than or equal to size |
| LTSIZE | size | File size is less than size |

### uScanFilter

**uScanFilter** can be initialized with separate components or with a string in the format: "*condition*:*details*".

**Test()** may be used to evaluate the filter condition.

**IsValid()** may be used to determine if the filter is valid.
- An invalid filter will cause scan execution to fail
- For example, an invalid regex or filesize is provided
 
```python
from m9lib import uScanFilter, uScanFilterCondition

# filter based on pattern
filter = uScanFilter(uScanFilterCondition.PATTERN, "*.txt")
filter = uScanFilter("PATTERN:*.txt")
filter = uScanFilter("PATTERN:*.txt;*.ini")
allgood = filter.IsValid()

# test the filter
match = filter.Test(r"c:\myfile.txt")
print(f"Match is {match}")
```

## Scanning

### uScanFiles

**uScanFiles** executes a scan operation using specified filters, returning a list of matching files.  Instantiate **uScanFiles** and call **Execute()** with scanning parameters.

**Execute(*RootFolder*, *ScanFilters*, *RecurseFolders*=False, *IgnoreFolders*=None)**
- *RootFolder*: Path to folder where scan begins
- *ScanFilters*: One or more filter conditions as a single filter in a string or a list of filter strings
- *RecurseFolders*: When True, recursively scan subfolders
- *IgnoreFolders*: Subfolders to ignore in the scan

Returns a list of (*name*, *path*), or *False* on error.  **Execute()** will fail if any filters were invalid.

These results can be reorganized by folder path using **OrganizeFilesByPath()**.

**uScanFiles.OrganizeFilesByPath(*Files*)**
- Reorganizes a list returned by **Execute()** to (*folderpath*, [*file1*, *file2*, ..])

```python
scan = uScanFiles()

# find all text files in the root folder
result = scan.Execute(r"c:\test", "PATTERN:*.txt")

# find all text files, recursively; include ini files
result = scan.Execute(r"c:\test", "PATTERN:*.txt;*.ini", RecurseFolders=True)

# find all text files greater than 5kb in size
result = scan.Execute(r"c:\test", ["PATTERN:*.txt", "GTSIZE:5kb"], RecurseFolders=True)

# find all text files greater than 5kb in size in a Config folder
result = scan.Execute(r"c:\test", ["PATTERN:*.txt", "GTSIZE:5kb", "P_PATTERN:Config"], RecurseFolders=True)

# reorganize results by folder
result_bypath = uScanFiles.OrganizeFilesByPath(result)
```
  
### uScanFolders

**uScanFolders** follows the same rules as **uScanFiles**, but returns a list of folders intead of files.

```python
scan = uScanFolders()

# find all bin folders in the root folder
result = scan.Execute(r"c:\test", "PATTERN:bin")

# find all folders starting with te, recursively
result = scan.Execute(r"c:\test", "PATTERN:te*", RecurseFolders=True)

# find all folders named bin under a parent folder that has te in the name
result = scan.Execute(r"c:\test", ["PATTERN:bin", "P_REGEX:.+te.+"], RecurseFolders=True)
```

### IgnoreFolders

*IgnoreFolders* can be a string or a list of strings (case insensitive). It can specify a path from the root, or a subpath within root.
- For example: Execute(r"c:\test", IgnoreFolders=r"c:\test\sub") will ignore:
  - "c:\test\sub"
- For example: Execute(r"c:\test", IgnoreFolders="sub") will ignore:
  - "c:\test\sub"
  - "c:\test\sub\one"
  - "c:\test\sub\two"
  - "c:\test\orange\sub"
  - "c:\test\orange\sub\one"
- For example: Execute(r"c:\test", IgnoreFolders=r"sub\one") will ignore:
  - "c:\test\sub\one"
  - "c:\test\orange\sub\one"

*IgnoreFolders* is evaluated using regex, and so may contain regex expressions.  As part of the normal evaluation of this path string, any internal slashes are converted to a double-slash to be interpreted properly by regex.  If you wish to use a regex expression that includes a backslash as an escape character, then you must turn of this automated processing by prefixing your ignore folders string with "REGEX:" and escape any backslash characters yourself.
- The following are equivalent:
  - r"sub\one"
  - r"$sub\\one"
- Here is a regex example that will also ignore "sub\one":
  - r"s.*b\o(m|n)e"
