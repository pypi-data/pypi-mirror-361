
# uCSV

Read and write simple CSV files.

## CSV formats

### Define a CSV format

Defining a CSV format helps in reading/writing CSV files.

**uCSVFormat(*Header*=True, *Delimiter*=',', *Identity*:uCSVIdentity=uCSVIdentity.NONE)**
- *Header*: True when there is a header row
- *Delimiter*: Specifies the delimiter to use when read/writing files
- *Identity*: Enables additional features based on identity columns

*Identity* supports three modes:
  - uCSVIdentity.NONE: There is no identity column
  - uCSVIdentity.ID_ONLY: The first column is an identity column
  - uCSVIdentity.ID_DATE: The first column is an identity column; the second column is a timestamp column

When using the first column as an identity column:
  - Uniqueness is enforced when reading files / adding rows
  - A row can be accessed using an id

When using the second column as a timestamp column:
  - Second column is enforced to be a timestamp in the format "%Y-%m-%d %H:%M:%S"

Use **SetColumns(*Columns*)** to set the column names (and count of columns) for a format
  - *Columns* is a list of column names
  - These column names will be written and matched to the header of CSV files

### Reading format from a file

You can create a **uCSVFormat** object from an existing file.

**uCSVFormat.ReadFormat(*Filepath*, *Header*=True, *Delimiter*=',')**
  - Reads the first line of a file and returns a **uCSVFormat** object

When reading an existing CSV file, this step is not required.  Just create a **uCSV** file without a format and load the file (example below).

### Testing the format

You may test a format against an existing file to see if there is a match.

**TestFormat(*Filepath*)**
  - Opens a file and checks to see if file format is compatible
  - Returns True if there is a format match
  - If the file is empty, returns True
  - If their is a mismatch in the format, returns a string describing the problem

## uCSV

### Instantiation

A CSV object is initialized with a format.

If a format is not provided, it can be established later by calling **ResetFormat()** or **ReadFile()**.

**uCSV(*Format*=None)**
  - Initialize with a format

**ResetFormat(*Columns*, *Header*=True, *Delimiter*=',', *Identity*:uCSVIdentity=uCSVIdentity.NONE)**
  - In case you want to reset the format after creation, or without instantiating a **uCSVFormat** object
  - Clears all rows

### Add rows

**AddRow(*Row*, *Replace*=False)**
  - Adds a single row using a list of values
  - Row must confirm to the format
  - Identity must be unique if Identity is ID_ONLY or ID_DATE, unless *Replace* is True, in which case the row will be replaced
  - Returns an id when using an identity column, or None on success
  - Returns False on failure

**AddRows(*Rows*, *Replace*=False)**
  - Calls **AddRow()** for each list entry in *Rows*
  - Returns len(Rows) on success
  - Returns False on failure; In case of failure, a partial number of rows may have been added

### Data access

**GetRowCount()**
  - Return the number of rows

**GetRow(*Index*)**
  - Returns a row by index, or None if Index is not valid

**GetRowById(*RowId*)**
  - Returns a row by id, or None if not found (or no identity defined)

**GetRows()**
  - Access all rows; a list of a list

### Data search

**SearchRows(*Conditions*, *And*=True)** returns a list of rows that satisfy a match condition
  - *Conditions*: a list of (*column*, *condition*)
    - *column*: can be a column name or index
    - *condition*: if starting with "REGEX:" use this regular expression; if starting with a logical symbol, a numerical comparison; otherwise, a literal comparison
  - *And*: when True, all conditions must match; when False, only one condition must match
  - Supported logical symbols are =, ==, !=, <, <=, >, >=; Comparisons work against strings that can be converted to float
  - Returns a list of matching rows
  - Returns False when there is an error in the condition specification

```python
# find first names of Alice
SearchRows([('name', "Alice")])
# find first names staring with A; regex example
SearchRows([('name', "REGEX:[aA].+")])
# find values in column 3 greather than 10
SearchRows([(3, ">10")])
# find cost values > 10.5 AND second column is "yes"
SearchRows([('cost', ">10.5"), (2, "yes")])
# find cost values > 10.5 OR second column is "yes"
SearchRows([('cost', ">10.5"), (2, "yes")], And=False)
```

### Reading CSV

**ReadFile(*Filepath*, *ReadMode*=uCSVReadMode.CONFORM)**
  - Reads a CSV file
  - Supports the following modes:
    - uCSVReadMode.RESET: Clear row data before reading
    - uCSVReadMode.CONFORM: File must conform to existing format.  Replaces any rows stored in this object
    - uCSVReadMode.ADDROWS: File must conform to existing format.  Appends rows stored in this object

If no format was specified for the uCSV, the format is read from the file by reading the first line. In this case, the values *Header*, *Delimiter*, and *Identity* are utilized when establishing a new format.

```python
# read a CSV file, accepting file format
csv = uCSV()
csv.ReadFile(r"c:\MyFile.csv")
```

```python
# read a CSV file of a specified format
csv_format = uCSVFormat(Identity=uCSVIdentity.ID_ONLY)
csv_format.SetColumns(['id', 'name', 'notes'])
csv = uCSV(csv_format)
csv.ReadFile(r"c:\MyFile.csv", uCSVReadMode.CONFORM)
# find row with id 99
row = csv.GetRowById(99)
# this is equivalent, since all ids are converted to str
row = csv.GetRowById("99")
```

### Writing CSV

**WriteFile(*Filepath*, *WriteMode*=uCSVWriteMode.OVERWRITE)**
  - Writes a CSV file
  - Supports the following write modes:
    - uCSVWriteMode.CREATE: Creates a file, writing a header according to the format; will not overwrite
    - uCSVWriteMode.OVERWRITE: Overwrites a file, or creates a file if it doesn't exist
    - uCSVWriteMode.APPEND: Append to an existing file, or creates a file if it doesn't exist; If the file exists and the format does not match, the write will fail
  - Returns the number of rows written (excluding header)

```python
# write a CSV file of a specified format
csv_format = uCSVFormat(Identity=uCSVIdentity.ID_ONLY)
csv_format.SetColumns(['id', 'name', 'notes'])
csv = uCSV(csv_format)
csv.AddRow(['1', 'Lisa', 'Engineer'])
csv.AddRow(['2', 'Matt', 'The Robot'])
csv.AddRow(['5', 'Gerard', 'Wandered in'])
csv.WriteFile(r"MyFile.csv", uCSVWriteMode.OVERWRITE)
```

## Use example

- Write a new CSV file
- Append a row to the CSV file
- Read the CSV, accepting format
- Demonstrate search capabilities

```python
from m9lib import uCSV, uCSVFormat, uCSVWriteMode, uCSVIdentity

# write a CSV file of a specified format
csv_format = uCSVFormat(Identity=uCSVIdentity.ID_ONLY)
csv_format.SetColumns(['id', 'name', 'notes'])
csv = uCSV(csv_format)
csv.AddRow(['1', 'Lisa', 'Engineer'])
csv.AddRow(['2', 'Matt', 'The Robot'])
csv.AddRow(['5', 'Gerard', 'Wandered in'])
ret = csv.WriteFile("MyFile.csv", uCSVWriteMode.OVERWRITE)
print(f"WriteFile returned: {ret}")

# to add a single row, first read the format, then append a row
csv_format = uCSVFormat.ReadFormat("MyFile.csv", Identity=uCSVIdentity.ID_ONLY)
csv = uCSV(csv_format)
csv.AddRow(['7', 'Marin', 'Cosplayer'])
ret = csv.WriteFile("MyFile.csv", uCSVWriteMode.APPEND)
print(f"WriteFile returned: {ret}")

# read the CSV, accepting format
csv = uCSV()
ret = csv.ReadFile("MyFile.csv", Identity=uCSVIdentity.ID_ONLY)
print(f"ReadFile returned: {ret}")
print(f"Row count: {csv.GetRowCount()}")

# get row based on id
print("Search (id=2): " + str(csv.GetRowById(2)))
# search for rows - empty search condition
print("Search (empty): " + str(csv.SearchRows([])))
# search for rows - literal
print("Search (name=Matt, id=1): " + str(csv.SearchRows([('name', 'Matt'), ('id', '1')], And=False)))
# search for rows - use regular expression
print("Search (contains ar): " + str(csv.SearchRows([('name', 'REGEX:.*ar.*')])))
```