# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

import os
import fnmatch
import re

from .u_format import uStringFormat
from .u_folder import uFolder

from enum import Enum
class uScanFilterCondition(Enum):
    NONE = 0        # always fails
    ISFILE = 1      # is a file
    ISFOLDER = 2    # is a folder
    PATTERN = 3     # matches specified pattern
    REGEX = 4       # matches regex
    P_PATTERN = 5   # parent folder matches specified pattern
    P_REGEX = 6     # parent folder matches regex
    GTSIZE = 7      # size greater than or equal to specified bytes, kb, mb, gb
    LTSIZE = 8      # size less than specified bytes, kb, mb, gb
    PN_PATTERN = 15 # parent folder does not match specified pattern
    PN_REGEX = 16   # parent folder does not match regex
    ERROR = -1

class uScanFilter:
    def __init__(self, Condition:uScanFilterCondition|str=uScanFilterCondition.NONE, Details:str|int=None, Include:bool=True):
        '''
        Establishes a filter for a scan operation.  A filter selects files or folders to include or exclude from the scan.
        - **Condition**: *ISFILE*, *ISFOLDER*, *PATTERN*, *REGEX*, *P_PATTERN*, *P_REGEX*, *GTSIZE*, *LTSIZE*, *PN_PATTERN*, *PN_REGEX*
        - **Details**: a match value, depending on **Condition**
        - **Include**: when *True*, a match selects the file/folder.  When False, it is *excluded*

        **Details** is based on the **Condition**.
        - <u>Pattern</u>: a file mask.  May include multiple file masks separated by semi-colons.  For example: "*.jpg;*.jpeg"
        - <u>Regex</u>: a regular expression
        - <u>Size</u>: file size, in bytes with units.  For example: "5kb"

        - If **Condition** is a string, filter values are specified as  colon-separated values in the format *condition*:*details*[:*include*].  *include* is True when not specified.
        '''
        self.Include = False
        self.Condition = uScanFilterCondition.ERROR
        self.Details = None
        try:
            if isinstance(Condition, uScanFilterCondition):
                self.Include = Include
                self.Condition = Condition
                self.Details = Details
                if self.Condition == uScanFilterCondition.REGEX or self.Condition == uScanFilterCondition.P_REGEX:
                    self.Details = re.compile(Details, re.IGNORECASE)
                elif self.Condition == uScanFilterCondition.GTSIZE or self.Condition == uScanFilterCondition.LTSIZE:
                    self.Details = uStringFormat.ParseBytes(Details)
                    if self.Details is False:
                        self.Condition = uScanFilterCondition.ERROR
            elif isinstance(Condition, str):
                self.__configure(Condition)
        except:
            self.Condition = uScanFilterCondition.ERROR

    def IsValid(self)->bool:
        return self.Condition != uScanFilterCondition.ERROR

    def Test(self, Filepath:str)->bool:
        '''
        Test the filter condition on a **Filepath**.
        
        Returns *True* if the filter would include the **Filepath** based on criteria.
        '''
        # returns True if the filter condition matches
        match = False
        match self.Condition:
            case uScanFilterCondition.ISFILE:
                match = os.path.isfile(Filepath)
            case uScanFilterCondition.ISFOLDER:
                match = os.path.isdir(Filepath)
            case uScanFilterCondition.PATTERN:
                match = self.__pattern_match(Filepath)
            case uScanFilterCondition.REGEX:
                match = self.__regex_match(Filepath)
            case uScanFilterCondition.P_PATTERN:
                match = self.__p_pattern_match(Filepath)
            case uScanFilterCondition.PN_PATTERN:
                match = not self.__p_pattern_match(Filepath)
            case uScanFilterCondition.P_REGEX:
                match = self.__p_regex_match(Filepath)
            case uScanFilterCondition.PN_REGEX:
                match = not self.__p_regex_match(Filepath)
            case uScanFilterCondition.GTSIZE:
                match = (os.path.getsize(Filepath) >= self.Details)
            case uScanFilterCondition.LTSIZE:
                match = (os.path.getsize(Filepath) < self.Details)

        return (self.Include == match)
    
    def __pattern_match(self, in_filepath):
        name = os.path.basename(in_filepath)
        s = self.Details.split(';')
        for p in s:
            if fnmatch.fnmatch(name, p):
                return True
        return False
    
    def __p_pattern_match(self, in_filepath):
        return self.__pattern_match(os.path.dirname(in_filepath))
    
    def __regex_match(self, in_filepath):
        name = os.path.basename(in_filepath)
        return (self.Details.match(name) is not None)
    
    def __p_regex_match(self, in_filepath):
        return self.__regex_match(os.path.dirname(in_filepath))
    
    def __configure(self, in_config):
        self.Include = True
        self.Condition = uScanFilterCondition.ERROR
        self.Details = None
        l = in_config.split(':')
        if len(l)>2 and l[2].lower()=='false':
            self.Include = False
        if len(l)>0:
            cond = l[0].upper()
            if cond == 'ISFILE':
                self.Condition = uScanFilterCondition.ISFILE
            elif cond == 'ISFOLDER':
                self.Condition = uScanFilterCondition.ISFOLDER
            elif cond == 'GTSIZE' and len(l)>1 and len(l[1])>0:
                self.Condition = uScanFilterCondition.GTSIZE
                self.Details = uStringFormat.ParseBytes(l[1])
            elif cond == 'LTSIZE' and len(l)>1 and len(l[1])>0:
                self.Condition = uScanFilterCondition.LTSIZE
                self.Details = uStringFormat.ParseBytes(l[1])
            elif cond == 'PATTERN' and len(l)>1 and len(l[1])>0:
                self.Condition = uScanFilterCondition.PATTERN
                self.Details = l[1]
            elif cond == 'P_PATTERN' and len(l)>1 and len(l[1])>0:
                self.Condition = uScanFilterCondition.P_PATTERN
                self.Details = l[1]
            elif cond == 'PN_PATTERN' and len(l)>1 and len(l[1])>0:
                self.Condition = uScanFilterCondition.PN_PATTERN
                self.Details = l[1]
            elif cond == 'REGEX' and len(l)>1 and len(l[1])>0:
                self.Condition = uScanFilterCondition.REGEX
                self.Details = re.compile(l[1], re.IGNORECASE)
            elif cond == 'P_REGEX' and len(l)>1 and len(l[1])>0:
                self.Condition = uScanFilterCondition.P_REGEX
                self.Details = re.compile(l[1], re.IGNORECASE)
            elif cond == 'PN_REGEX' and len(l)>1 and len(l[1])>0:
                self.Condition = uScanFilterCondition.PN_REGEX
                self.Details = re.compile(l[1], re.IGNORECASE)

class uScanFF(Enum):
    ALL = 0,
    FILES_ONLY = 1,
    FOLDERS_ONLY = 2

class uScan:
    def __init__(self, RootFolder=None, RecurseFolders=True, ScanFF=uScanFF.FILES_ONLY, IgnoreFolders:str|list=None):
        '''
        Initializes a scan operation.  Scan parameters can be established here or during execution.
        - **RootFolder**: root folder for scan operation
        - **RecurseFolders**: *True* to scan subfolders
        - **ScanFF**: *ALL*, *FILES_ONLY*, or *FOLDERS_ONLY*
        - **IgnoreFolders**: a string or list of strings; results under a matching folder name will be ignored
        '''
        # IgnoreFolders can be a string or list of strings .. any results found under a folder exactly matching an ignored folder name will be excluded from results
        # IgnoreFolders is only relevant when RecurseFolders is True
        self.root_folder = None
        self.scan_filters = []
        self.init_parameters(True, RootFolder, RecurseFolders, ScanFF, IgnoreFolders)

    def ClearScanFilters(self):
        '''
        Clear all filters.
        '''
        self.scan_filters = []

    def AddScanFilter(self, Filter:uScanFilter|str):
        '''
        **Filter** can be a **uScanFilter** or string.
        '''
        if isinstance(Filter, uScanFilter):
            self.scan_filters.append(Filter)
        elif isinstance(Filter, str):
            self.scan_filters.append(uScanFilter(Condition=Filter))

    def ClearIgnoreFolders(self):
        '''
        Clears ignore folders.
        '''
        self.ignore_folders = None

    def SetIgnoreFolders(self, IgnoreFolders:str|list):
        '''
        Set ignore folders.  **IgnoreFolders** can be a string or list of strings.
        '''
        self.ignore_folders = IgnoreFolders

    def IsValid(self):
        '''
        Returns *True* when there is at least one filter, and all filters are valid.

        Even a single invalid filter will cause execution to fail.
        '''
        if len(self.scan_filters)==0:
            return False
        
        for filter in self.scan_filters:
            if filter.IsValid() is False:
                return False
            
        return True

    def Execute(self, RootFolder:str=None, RecurseFolders:bool=None, ScanFF:uScanFF=None, IgnoreFolders:list|str=None):
        # executes a folder scan operation
        # if any parameters are specified, current parameter will be replaced
        self.init_parameters(False, RootFolder, RecurseFolders, ScanFF, IgnoreFolders)
        self.init_ignorefolders()

        # check for invalid path
        if os.path.isdir(self.root_folder) is False:
            return False
        
        # check for condition of a filter that errored out (bad regex)
        if self.IsValid() is False:
            return False

        try:
            self.imp_pre_execute(self.root_folder, self.recurse_folders, self.scan_ff, self.ignore_folders)
            if self.scan_ff is not None:
                if self.recurse_folders is False:
                    ldir = os.listdir(self.root_folder)
                    for entry in ldir:
                        if self.scan_ff == uScanFF.ALL or (self.scan_ff == uScanFF.FILES_ONLY and os.path.isfile(os.path.join(self.root_folder, entry))) or (self.scan_ff == uScanFF.FOLDERS_ONLY and os.path.isdir(os.path.join(self.root_folder, entry))):
                            self.__process_entry(self.root_folder, entry)
                else:
                    for root, dirs, files in os.walk(self.root_folder):
                        if self.__skip_folder (root) is False:
                            if (self.scan_ff == uScanFF.ALL or self.scan_ff == uScanFF.FILES_ONLY):
                                for entry in files:
                                    self.__process_entry(root, entry)
                            if (self.scan_ff == uScanFF.ALL or self.scan_ff == uScanFF.FOLDERS_ONLY):
                                for entry in dirs:
                                    self.__process_entry(root, entry)
            return True
        except:
            return False

    def imp_pre_execute(self, RootFolder, RecurseFolders, ScanFF, IgnoreFolders):
        # called at the start of execution
        pass

    def imp_found_file(self, in_folderpath, in_filename):
        # called when file element matched
        # ext will be forced to lower without .
        pass

    def imp_found_folder(self, in_folderpath, in_foldername):
        # called when folder element matched
        # ext will be forced to lower without .
        pass

    def init_parameters(self, Set, RootFolder, RecurseFolders, ScanFF, IgnoreFolders):
        # Set means to set regardless of None, otherwise replace if not None
        if Set is True:
            self.root_folder = RootFolder
            self.recurse_folders = RecurseFolders
            self.scan_ff = ScanFF
            self.ignore_folders = IgnoreFolders
        else:
            if RootFolder is not None:
                self.root_folder = RootFolder
            if RecurseFolders is not None:
                self.recurse_folders = RecurseFolders
            if ScanFF is not None:
                self.scan_ff = ScanFF
            if IgnoreFolders is not None:
                self.ignore_folders = IgnoreFolders

    def init_ignorefolders(self):
        self.re_ignore_folders = None
        if self.ignore_folders is not None:
            iflist = []
            if isinstance(self.ignore_folders, str) and len(self.ignore_folders)>0:
                iflist.append(self.ignore_folders)
            elif isinstance(self.ignore_folders, list):
                for f in self.ignore_folders:
                    if isinstance(f, str) and len(f)>0:
                        iflist.append(f)

            ifstr = None
            for f in iflist:
                if f.startswith("$"):
                    f2 = f[1:]
                else:
                    f2 = f.replace("\\", "\\\\")
                restr = "(^|(\\\\))" + f2 + "($|(\\\\))"
                if ifstr is None:
                    ifstr = restr
                else:
                    ifstr = ifstr + "|" + restr

            if ifstr is not None:
                self.re_ignore_folders_str = ifstr
                self.re_ignore_folders = re.compile(ifstr, re.IGNORECASE)

    def __skip_folder(self, in_folder):
        if self.re_ignore_folders is None:
            return False

        if self.re_ignore_folders.search(in_folder) is None:
            return False

        return True
    
    def __process_entry(self, in_path, in_name):
        filepath = os.path.join(in_path, in_name)
        for fi in self.scan_filters:
            if fi.Test(filepath) is False:
                return None

        if os.path.isfile(filepath):
            self.imp_found_file(in_path, in_name)
        else:
            self.imp_found_folder(in_path, in_name)

class uScanFiles(uScan):
    def __init__(self):
        super().__init__()
        self.result = None

    def Execute(self, RootFolder:str, ScanFilters:str|list|uScanFilter, RecurseFolders:bool=False, IgnoreFolders:str|list=None):
        '''
        Performs a folder scan starting from **RootFolder**.
        - **ScanFilters*: a string or **uScanFilter**, or a list thereof
        - **RecurseFolders**: when *True*, scan subfolders
        - **IgnoreFolders**: a string or list of folders to ignore when recursing subfolders

        Returns a list of (*filename*, *folderpath*), or False on error.
        '''
        self.ClearScanFilters()
        if isinstance(ScanFilters, str):
            self.AddScanFilter(ScanFilters)
        elif isinstance(ScanFilters, list):
            for filter in ScanFilters:
                self.AddScanFilter(filter)

        self.init_parameters(True, RootFolder, RecurseFolders, uScanFF.FILES_ONLY, IgnoreFolders)
        if super().Execute() is False:
            self.result = None
            return False
        
        result = self.result
        self.result = None
        return result
    
    @staticmethod
    def OrganizeFilesByPath(Files:list)->list:
        '''
        Reorganizes a list of (*name*, *path*) returned by Execute() by folder path.

        Returns a list of (*folderpath*, [*file1*, *file2*, ..]).

        An alias of uFolder.OrganizeFilesByPath().
        '''
        return uFolder.OrganizeFilesByPath(Files)

    def imp_pre_execute(self, RootFolder, RecurseFolders, ScanFF, IgnoreFolders):
        # called at the start of execution
        self.result = []

    def imp_found_file(self, in_folderpath, in_filename):
        # called when file element matched
        # ext will be forced to lower without .
        self.result.append((in_filename, in_folderpath))

class uScanFolders(uScan):
    def __init__(self):
        super().__init__()
        self.result = None

    def Execute(self, RootFolder:str, ScanFilters:str|list|uScanFilter, RecurseFolders:bool=False, IgnoreFolders:str|list=None):
        '''
        Performs a folder scan starting from **RootFolder**.
        - **ScanFilters*: a string or **uScanFilter**, or a list thereof
        - **RecurseFolders**: when *True*, scan subfolders
        - **IgnoreFolders**: a string or list of folders to ignore when recursing subfolders

        Returns a list of (*filename*, *folderpath*), or False on error.
        '''
        self.ClearScanFilters()
        if isinstance(ScanFilters, str):
            self.AddScanFilter(ScanFilters)
        elif isinstance(ScanFilters, list):
            for filter in ScanFilters:
                self.AddScanFilter(filter)

        self.init_parameters(True, RootFolder, RecurseFolders, uScanFF.FOLDERS_ONLY, IgnoreFolders)
        if super().Execute() is False:
            self.result = None
            return False
        
        result = self.result
        self.result = None
        return result

    @staticmethod
    def OrganizeFoldersByPath(Folders:list)->list:
        '''
        Reorganizes a list of (*name*, *path*) returned by Execute() by folder path.

        Returns a list of (*folderpath*, [*file1*, *file2*, ..]).

        An alias of uFolder.OrganizeFilesByPath().
        '''
        return uFolder.OrganizeFilesByPath(Folders)

    def imp_pre_execute(self, RootFolder, RecurseFolders, ScanFF, IgnoreFolders):
        # called at the start of execution
        self.result = []

    def imp_found_folder(self, in_folderpath, in_foldername):
        # called when file element matched
        # ext will be forced to lower without .
        self.result.append((in_foldername, in_folderpath))
