# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

import re

class uColor():
    def __init__(self, Red, Green, Blue):
        self.red = Red
        self.green = Green
        self.blue = Blue

    @staticmethod
    def CalcDifference(Color1, Color2, Percent):
        '''
        Calculate an intermediate color between two colors, returning **uColor**.
        '''
        return uColor(Color1.red + Percent * (Color2.red - Color1.red), Color1.green + Percent * (Color2.green - Color1.green), Color1.blue + Percent * (Color2.blue - Color1.blue))

    @staticmethod
    def CalcGradient(Color1, Color2, Steps)->list:
        '''
        Returns a list of **uColor**.
        '''
        g = []
        if Steps<2:
            g.append(Color1)
        else:
            for s in range(Steps):
                g.append(uColor.CalcDifference (Color1, Color2, s/(Steps-1)))
        return g
    
class uConsoleColor:
    # Colors tuned to system("color")
    _codes = None
    _re_format = None

    @classmethod
    def GetCode(cls, Color):
        """
        Get a console code by color name.  Returns an empty string if **Color** is not recognized.
        """
        cls.__init_colors()
        if Color in cls._codes:
            return cls._codes[Color]
        return ""
    
    @classmethod
    def __init_colors(cls):
        if cls._codes is None:
            cls._codes = {}
            cls._codes['END'] = '\33[0m'
            cls._codes['BOLD'] = '\33[1m'
            cls._codes['ITALIC'] = '\33[3m'
            cls._codes['UNDERLINE'] = '\33[4m'
            cls._codes['RED'] = '\33[31m'
            cls._codes['GREEN'] = '\33[32m'
            cls._codes['YELLOW'] = '\33[33m'
            cls._codes['BLUE'] = '\33[34m'
            cls._codes['VIOLET'] = '\33[35m'
            cls._codes['CYAN'] = '\33[36m'
            cls._codes['WHITE'] = '\33[37m'

            cls._codes['BG_RED'] = '\33[41m'
            cls._codes['BG_GREEN'] = '\33[42m'
            cls._codes['BG_YELLOW'] = '\33[43m'
            cls._codes['BG_BLUE'] = '\33[44m'
            cls._codes['BG_VIOLET'] = '\33[45m'
            cls._codes['BG_CYAN'] = '\33[46m'

            cls._codes['GREY'] = '\33[90m'
            cls._codes['LT_RED'] = '\33[91m'
            cls._codes['LT_GREEN'] = '\33[92m'
            cls._codes['LT_YELLOW'] = '\33[93m'
            cls._codes['LT_BLUE'] = '\33[94m'
            cls._codes['LT_VIOLET'] = '\33[95m'
            cls._codes['LT_CYAN'] = '\33[96m'
            cls._codes['BRIGHTWHITE'] = '\33[97m'

    @classmethod
    def Wrap(cls, String, Color):
        """
        Wrap a **String** in console codes based on **Color**.
        """
        return cls.GetCode(Color) + String + cls.GetCode("END")

    @classmethod
    def Format(cls, String, StripColors=False):
        """
        Format **String** by replacing [+COLOR] and [+] with console codes.

        For example: "[+RED]Roses[+]" returns the "Roses" wrapped in red console codes.

        When **StripColors** is *True*, markups are removed without inserting console codes.
        """
        def replacement(match):
            key = match.group(1)
            if key is None:
                key = 'END'
            return uConsoleColor.GetCode(key)
        
        def removal(match):
            return ""
        
        if cls._re_format is None:
            cls._re_format = re.compile(r'\[\+(\w+)?\]')

        if StripColors:
            return cls._re_format.sub(removal, String)
        
        return cls._re_format.sub(replacement, String)
    
    @classmethod
    def PrintTest(cls):
        """
        Prints recognized colors with color codes to the console.
        """
        cls.__init_colors()
        for code in list(cls._codes.keys()):
            if code not in ['END', 'BOLD', 'ITALIC', 'UNDERLINE']:
                print(cls.Wrap(code, code))

    def __init__(self, System=None):
        uConsoleColor.__init_colors()
        self.system = System

    def Message(self, String):
        """
        Print a message to the console.  This message will undergo color formatting.
        """
        print(self.__sysstr() + uConsoleColor.Format(String))

    def Warning(self, String):
        """
        Print a warning message to the console.  This message will be light red.
        """
        print(self.__sysstr() + uConsoleColor.Wrap("[WARNING] " + String, "LT_RED"))

    def Header(self, String=None):
        """
        Print a formated header string to the console.
        """
        hs = ""
        if self.system is not None:
            hs += uConsoleColor.Wrap(self.system, "VIOLET")
        if self.system is not None and String is not None:
            hs += ": "
        if String is not None:
            hs += uConsoleColor.Wrap(String, "LT_VIOLET")
        print ("*** "+hs+" ***")

    def __sysstr(self, Color="BLUE", Prefix="", Postfix=": "):
        if self.system is not None:
            return Prefix+uConsoleColor.Wrap(self.system, Color)+Postfix
        return ""
