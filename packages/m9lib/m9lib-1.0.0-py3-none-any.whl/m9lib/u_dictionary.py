# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

from .u_format import *
from .u_type import uType

class uDictionary:
    
    def __init__(self, Dict={}):
        '''
        Initialize with a dict or uDictionary.
        '''
        if isinstance(Dict, dict):
            self.dict = Dict.copy()
        elif isinstance(Dict, uDictionary):
            self.dict = Dict.GetDictionary()
        else:
            self.dict = {}

    def Copy(self):
        '''
        Performs a shallow copy.
        '''
        return uDictionary(self.dict.copy())
    
    def GetKeys(self):
        return list(self.dict.keys())
        
    def GetValue(self, Name, Default=None):
        if Name in self.dict:
            return self.dict[Name]
        return Default

    def GetNumber(self, Name, Default=None):
        return uType.ConvertToInt(self.GetValue(Name, Default))
    
    def GetFloat(self, Name, Default=None):
        return uType.ConvertToFloat(self.GetValue(Name, Default))
    
    def GetBool(self, Name, Default=None):
        return uType.ConvertToBool(self.GetValue(Name, Default))
    
    def GetList(self, Name, Separator=","):
        return uType.ConvertToList(self.GetValue(Name), Separator)
    
    def SetValue(self, Name, Value):
        # set specified value
        self.dict[Name] = Value
        
    def ClearValue(self, Name):
        '''
        Remove the specified value.
        '''
        if Name in self.dict:
            del self.dict[Name]

    def HasValue(self, Name):
        return Name in self.dict
            
    def MergeValues(self, Dict, Overwrite=False):
        '''
        Takes a **dict** or **uDictionary**.

        Merges **dict** into current dictionary.

        If there is a confict on a given entry, only sets that value when **Overwrite** is *True*.
        '''
        d = None
        if isinstance(Dict, dict):
            d = Dict
        elif isinstance(Dict, uDictionary):
            d = Dict.GetDictionary(False)
        else:
            return

        for key in d:
            if not (Overwrite==False and key in self.dict):
                self.dict [key] = d [key]
            
    def GetDictionary(self, Copy=True)->dict:
        '''
        Returns the internal **dict**, or a **Copy** of this **dict**.
        '''
        # Gets the internal python dictionary
        # Reference to internal, unless copied
        if Copy:
            return self.dict.copy()
        return self.dict
