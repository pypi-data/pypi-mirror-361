# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

import os, re
from enum import Enum
from datetime import datetime
from .u_format import uStringFormat
from .u_type import uType

class uCSVIdentity(Enum):
    NONE = 0        # no identity column
    ID_ONLY = 1     # first column is an identifier
    ID_DATE = 2     # first column id, and second column is a date

class uCSVWriteMode(Enum):
    CREATE = 0      # create only -- fail if exists
    OVERWRITE = 1   # overwrite if exists
    APPEND = 2      # append if exists -- fail on csv format mismatch

class uCSVReadMode(Enum):
    RESET = 0       # reset format columns -- does not require columns to be defined
    CONFORM = 1     # confirm to format columns -- requires columns to be defined
    ADDROWS = 2     # confirm to format columns, but append data to existing rows

class uCSVFormat:

    def __init__(self, Header=True, Delimiter=',', Identity:uCSVIdentity=uCSVIdentity.NONE):
        '''
        - **Header**: first row in file is a header row.
        - **Delimiter**: delimiter character
        - **Identity**: special treatment for left-most columns.

        **Identity** is one of:
        - *uCSVIdentity.NONE*: no special treatment
        - *uCSVIdentity.ID_ONLY*: first column is a unique id
        - *uCSVIdentity.ID_DATE*: first column is a unique id; second column is a date-time
        '''
        self.Header = Header              # include header when read/writing files
        self.Delimiter = Delimiter      # delimiter when read/writing files
        self.Identity = Identity        # includes identity/date columns
        self.Columns = None             # list of column names

    def HasIdentity(self)->bool:
        '''
        Returns *True* when the first column is a unique id.
        '''
        return self.Identity == uCSVIdentity.ID_ONLY or self.Identity == uCSVIdentity.ID_DATE

    def SetColumns(self, Columns:list|str):
        '''
        Set columns using a list or comma-delimited string.
        '''
        self.Columns = uType.ConvertToList(Columns)

    def HasColumns(self)->bool:
        '''
        One or more columns have been configured.
        '''
        return self.Columns is not None and isinstance(self.Columns, list) and len(self.Columns)>0
    
    def ColumnCount(self)->int:
        '''
        Returns count of columns, or *None* if columns have not been configured.
        '''
        if self.Columns is None:
            return None
        return len(self.Columns)
    
    def GetColumnIndex(self, Column:str):
        '''
        Returns the index of a named column, or *None* of **Column** is not recognized.
        '''
        if self.Columns is not None:
            col = Column.lower()
            for i in range(len(self.Columns)):
                if self.Columns[i].lower() == col:
                    return i

        return None
    
    def TestFormat (self, Filepath:str)->bool|str:
        '''
        Return *True* if specified file matches defined format by opening the file and reading the first line.
        - Able to open file
        - Column count matches
        - If there is a header, column names match <u>identically</u>

        If the file is empty, a *True* is returned.

        Otherwise, returns a helpful string indicating the reason for failure.
        '''
        try:
            file = open(Filepath, 'r')
        except:
            return "Unable to open file"
        
        l = []
        try:
            line = file.readline().strip('\r\n')
            l = uStringFormat.Strip(line.split(self.Delimiter))
        except:
            pass
        
        file.close()
        
        if l==['']:
            return True # empty file
        
        if len(l)!=self.ColumnCount():
            return "Column count mismatch"
        
        if self.Header is True:
            if l != self.Columns:
                return "Column headers do not match"

        return True

    @staticmethod
    def ReadFormat(Filepath, Header=True, Delimiter=',', Identity:uCSVIdentity=uCSVIdentity.NONE):
        '''
        Create a new **uCSVFormat** object by opening a CSV file and reading the format from the first line.
        '''
        file = None
        try:
            format = uCSVFormat(Header=Header, Delimiter=Delimiter, Identity=Identity)
            file = open(Filepath, 'r')
            line = file.readline().strip('\r\n')
            file.close()
            file = None
            if len(line)>0:
                columns = []
                l = uStringFormat.Strip(line.split(format.Delimiter))
                if format.Header:
                    columns = l
                else:
                    le = len(l)
                    for index in range(le):
                        columns.append(f"Column {index+1}")

                format.SetColumns(columns)
                return format

        except:
            if file is not None:
                file.close()

        return False        

class uCSV:

    def __init__(self, Format:uCSVFormat=None):
        '''
        Initializes **uCSV** with a **Format**.

        If format is not specified, format can be established by **ResetFormat()** or **ReadFile()**.
        '''
        self.format = Format
        self.__reset_rows()

    def ResetFormat(self, Columns:list, Header=True, Delimiter=',', Identity:uCSVIdentity=uCSVIdentity.NONE):
        self.format = uCSVFormat(Header, Delimiter, Identity)
        self.format.SetColumns(Columns)
        self.__reset_rows()

    def AddRow(self, Row:list|str, Replace=False)->bool|str:
        '''
        **Row** is a list or comma-delimited string matching existing format.

        If identity is *uCSVIdentity.ID_ONLY* or *uCSVIdentity.ID_DATE*, the first column is interpreted as a row id.  In this case, when the identity already exists:
        - If **Replace** is *True*, the identity row will be replaced
        - If **Replace** is *False*, the row will not be added

        If identity is *uCSVIdentity.ID_DATE*, the second column is a SQL-date string or a **datetime** object.

        Returns :
        - *False* when **Row** format does not match, or the identity exists and **Replace** is *False*
        - *True* when **Row** was added, and there is no identity
        - Returns an id string when **Row** was added, and there is an identity 
        '''

        if self.format is None:
            return False    # no format set
        
        Row = uType.ConvertToList(Row)
        if Row is None or isinstance(self.format.Columns, list) is False or len(Row)==0:
            return False    # no data provided
        
        if len(Row) != self.format.ColumnCount():
            return False    # column count mismatch

        rowid = True
        replaceidx = None
        if self.format.HasIdentity():
            rowid = Row[0]
            if rowid in self.ids:
                if Replace is False:
                    return False    # identity exists
                
                replaceidx = self.ids[rowid]
                
        if self.format.Identity == uCSVIdentity.ID_DATE:
            # second column must be a valid timestamp
            if isinstance(Row[1], datetime) is False:
                try:
                    Row[1] = datetime.strptime(Row[1], '%Y-%m-%d %H:%M:%S')
                except:
                    return False    # invalid timestamp format

        if replaceidx is not None:
            self.rows[self.ids[rowid]] = Row
        else:
            if rowid is not True:
                self.ids[rowid] = len(self.rows)
            self.rows.append(Row)

        return rowid

    def AddRows(self, Rows, Replace=False):
        '''
        Returns a count of rows that were added.

        Returns False if any rows couldn't be added.
        '''
        if self.format is None:
            return False
        
        for row in Rows:
            if self.AddRow(row, Replace) is False:
                return False
            
        return len(Rows)
    
    # data access
    
    def GetRowCount(self):
        '''
        Returns count of rows.
        '''
        return len(self.rows)
    
    def GetRow(self, Index):
        '''
        Returns a row as a list of columns, or None if Index is invalid.
        '''
        return self.rows[Index] if (Index>=0 and Index<len(self.rows)) else None

    def GetRowById(self, RowId):
        '''
        Returns row by id, when an identity has been configured.
        '''
        if self.format is None:
            return False
        
        if self.format.HasIdentity():
            RowId = str(RowId)
            if RowId in self.ids:
                return self.rows[self.ids[RowId]]
            
        return None

    def GetRows(self):
        '''
        Returns all rows
        '''
        return self.rows
    
    def SearchRows(self, Conditions:list, And=True):
        '''
        Performs a search of rows and returns matching rows.  **Conditions** is a list of column conditions as (*column*, *condition*).
        - *column* can be a column name or column index
        - if *condition* starts with "REGEX:", it is a regex condition
        - if *condition* starts with =, <, >, <=, >=, != then the value is interpreted as a float and compared
        - Otherwise, *condition* is interpreted as a literal match
        When **And** is True, all conditions must be true, otherwise any condition can be true.
        '''

        # no conditions returns no results
        if len(Conditions) == 0:
            return []

        # transform conditions
        clist=[]
        for cond in Conditions:
            centry = None
            if cond[1].startswith ("REGEX:"):
                centry = {'mode':'regex', 're':re.compile(cond[1][6:])}
            elif cond[1][:2] in ['==', '!=', '>=', '<=']:
                centry = {'mode':'float', 'co':cond[1][:2], 'num':self.__safe_num(cond[1][2:])}
            elif cond[1][0] in ['=', '>', '<']:
                centry = {'mode':'float', 'co':cond[1][:1], 'num':self.__safe_num(cond[1][1:])}
            else:
                centry = {'mode':'value', 'val':cond[1]}

            centry['col'] = None
            if isinstance(cond[0], str):
                centry['col'] = self.format.GetColumnIndex(cond[0])
            elif isinstance(cond[0], int):
                if cond[0]>=0 and cond[0] < self.format.ColumnCount():
                    centry['col'] = cond[0]

            if centry['col'] is None or ('num' in centry and centry['num'] is False):
                return False    # failed conditions

            clist.append(centry)

        match_rows = []

        try:
            if And is True: # AND conditions
                for row in self.rows:
                    cmatch = 0
                    for cond in clist:
                        if self.__match_condition(row, cond):
                            cmatch += 1
                        else:
                            break

                    if cmatch==len(clist):
                        match_rows.append(row)
            else:   # OR conditions
                for row in self.rows:
                    for cond in clist:
                        if self.__match_condition(row, cond):
                            match_rows.append(row)
                            break
        except:
            return False

        return match_rows

    def __safe_num(self, num):
        try:
            return float(num)
        except:
            return False
        
    def __match_condition(self, in_row, in_cond):
        if in_cond['mode']=='value':
            return (in_row[in_cond['col']] == in_cond['val'])
        elif in_cond['mode']=='regex':
            return in_cond['re'].match(str(in_row[in_cond['col']])) is not None
        elif in_cond['mode']=='float':
            num = self.__safe_num(in_row[in_cond['col']])
            if num is not False:
                match in_cond['co']:
                    case '=':
                        return num==in_cond['num']
                    case '==':
                        return num==in_cond['num']
                    case '!=':
                        return num!=in_cond['num']
                    case '>':
                        return num>in_cond['num']
                    case '>=':
                        return num>=in_cond['num']
                    case '<':
                        return num<in_cond['num']
                    case '<=':
                        return num<=in_cond['num']

        return False
    
    # file access

    def WriteFile(self, Filepath, WriteMode=uCSVWriteMode.OVERWRITE):
        '''
        Writes a CSV file.  Supports the following modes:
        - uCSVWriteMode.CREATE: Creates the file, but fails if it exists
        - uCSVWriteMode.OVERWRITE: Creates the file, overwriting if it exists
        - uCSVWriteMode.APPEND: Creates the file if it doesn't exist, appends if it does exist; file format must match

        Returns the number of rows written.
        '''

        # returns number of rows written
        # returns False on failure

        if self.format is None:
            return False # format not defined

        file = None
        try:
            if WriteMode == uCSVWriteMode.CREATE and os.path.isfile(Filepath):
                return False    # file exists failure
            
            if WriteMode == uCSVWriteMode.APPEND and os.path.isfile(Filepath):
                if self.format.TestFormat(Filepath) is not True:
                    return False

                # append to file
                file = open(Filepath, 'a', encoding='utf-8')
            else:
                # file doesn't exist
                file = open(Filepath, 'w', encoding='utf-8')

                # write header
                if self.format.Header is True:
                    self.__write_row (file, self.format.Columns)

            # file ready - write rows
            for row in self.rows:
                self.__write_row (file, row)

            file.close()

            return len(self.rows)
        except:
            if file is not None:
                file.close()

        return False

    def ReadFile(self, Filepath, ReadMode=uCSVReadMode.CONFORM, Header=True, Delimiter=',', Identity:uCSVIdentity=uCSVIdentity.NONE):
        '''
        Reads a CSV file.  Supports the following modes:
        - uCSVReadMode.RESET: Clears row data
        - uCSVReadMode.CONFORM: File must conform to existing format.  Replaces any rows stored in this object
        - uCSVReadMode.ADDROWS: File must conform to existing format.  Appends rows stored in this object

        If no format was specified for the uCSV, the format is read from the file by reading the first line.
        In this case, the values *Header*, *Delimiter*, and *Identity* are utilized when establishing a new format.
        '''
        # returns number of rows read, which is not the stored rows, depending on identity format
        # uCSVReadMode.RESET assumes that the file has a header with no identity column 
        # returns False on failure
        # empty file will return failure
        if os.path.isfile(Filepath) is False:
            return False # file does not exist
        
        if self.format is None:
            format = uCSVFormat.ReadFormat(Filepath, Header=Header, Delimiter=Delimiter, Identity=Identity)
            if isinstance(format, uCSVFormat):
                self.format = format
            else:
                return False # unable to read format
        elif (ReadMode == uCSVReadMode.CONFORM or ReadMode == uCSVReadMode.ADDROWS):
            if self.format.TestFormat(Filepath) is not True:
                return False # read mode requires a matching format

        if (ReadMode == uCSVReadMode.CONFORM or ReadMode == uCSVReadMode.RESET):
            self.__reset_rows()

        file = None
        ret = False
        try:
            file = open(Filepath, 'r')
            if self.format.Header is True:
                line = file.readline().strip('\r\n')
                if (ReadMode == uCSVReadMode.RESET):
                    l = line.split(self.format.Delimiter)
                    self.format.SetColumns(l)

            line = file.readline().strip('\r\n')
            while len(line)>0:
                l = line.split(self.format.Delimiter)
                if self.AddRow(l) is False:
                    raise Exception("CSV row does not match format")
                line = file.readline().strip('\r\n')

            ret = True

        except:
            pass

        if file is not None:
            file.close()

        return ret
    
    # private methods

    def __reset_rows(self):
        self.rows = []
        self.ids = None
        if self.format is not None and self.format.HasIdentity():
            self.ids = {}

    def __write_row (self, in_file, in_row):
        row = []
        for col in in_row:
            if isinstance(col, datetime):
                row.append(col.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                row.append(str(col))
        line = self.format.Delimiter.join(row)
        in_file.write(line + '\n')
