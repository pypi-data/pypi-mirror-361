# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

from .u_format import *

class uType:

    @staticmethod
    def ConvertToInt(Value:str)->int:
        '''
        Converts a string **Value** to an *int*.

        Returns *False* on error
        
        Returns *None* if **Value** is None or empty.
        '''
        if Value is None or Value=="":
            return None
        try:
            return int(Value)
        except:
            pass
        return False        

    @staticmethod
    def ConvertToFloat(Value:str)->float:
        '''
        Converts a string **Value** to an *int*.

        Returns *False* on error
        
        Returns *None* if **Value** is None or empty.
        '''
        if Value is None or Value=="":
            return None
        try:
            return float(Value)
        except:
            pass
        return False        

    @staticmethod
    def ConvertToBool(Value:str)->bool:
        '''
        Converts a **Value** to a *bool*.

        Returns *True* if **Value** is *True* or "true" (case-insensitive).

        Returns *False* otherwise.
        '''
        if Value is None or Value=="":
            return None
        if isinstance(Value, bool):
            return Value
        elif isinstance(Value, str):
            return Value.lower()=="true"
        return False

    @staticmethod
    def ConvertToList(Value:str|list, Separator=","):
        '''
        Converts a string **Value** to a *list*, or returns **Value** if it is a list.

        Returns *False* on failure.
        '''
        if Value is None:
            return None
        elif isinstance(Value, list):
            return Value
        elif isinstance(Value, str):
            return uStringFormat.Strip (Value.split (Separator))
        return False

    @staticmethod
    def SafeString(Value:str):
        '''
        Converts *Value* to a string.

        If *None*, returns an empty string.
        '''
        if Value is None:
            return ""
        return str(Value)