# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

from m9lib import uConsoleColor

class uFailures:
    _failures = []
    _print_failures = 0
    _suppress_c88 = True

    @classmethod
    def AddFailure(cls, Session, Context, Code, Failure):
        if cls._suppress_c88 and Code=="C88":
            return

        if not isinstance(Context, str):
            Context = Context.__class__.__name__
        cls.__print_failure(Context, Code, Failure)
        cls._failures.append((Session, Context, Code, Failure))

    @classmethod
    def __print_failure(cls, Context, Code, Failure):
        if cls._print_failures>0:
            if Context is None:
                contextstr = ""
            else:
                contextstr = f" [+CYAN]{Context}[+][+BLUE]:[+] "

            failure_string = f"[+BLUE][[+][+VIOLET]{Code}[+][+BLUE]][+]{contextstr}[+BLUE]{Failure}[+]"
            match cls._print_failures:
                case 1:
                    failure_string_stripped = uConsoleColor.Format(failure_string, True)
                    print(failure_string_stripped)
                case 2:
                    print(uConsoleColor.Format(failure_string))

    @classmethod
    def PrintFailures(cls, Print:bool=True, PrintColor:bool=True):
        '''
        Failures will be printed to the console.
        '''
        if Print:
            cls._print_failures = 2 if PrintColor else 1
        else:
            cls._print_failures = 0
    
    @classmethod
    def ClearFailures(cls, Session=None) -> None:
        if Session is None:
            cls._failures = []
        else:
            cls._failures = [f for f in cls._failures if f[0] != Session]

    @classmethod
    def HasFailures(cls, Session=None) -> bool:
        '''
        Returns *True* when there are failure strings available in **GetFailures()**.
        '''
        if Session is None:
            return len(cls._failures)>0
        
        if Session is not None and isinstance(Session, int) is False:
            Session = id(Session)
    
        failures = cls.GetFailures(Session, Reset=False)
        return len(failures)>0
    
    @classmethod
    def GetFailures(cls, Session=None, Reset=True) -> list:
        '''
        Returns a list of failures since the config file was loaded.

        Returns an empty list if there are no failures.

        If **Reset** is *True*, the internal failure list will clear.
        '''
        if Session is not None and isinstance(Session, int) is False:
            Session = id(Session)

        failures = [(f[1],f[2],f[3]) for f in cls._failures if Session is None or Session == f[0]]
        if Reset:
            cls.ClearFailures(Session)
        return failures
    
    @classmethod
    def TestFailures(cls, Failures, Session=None, Reset=True, Exclude:list=[]):
        try:
            test = False
            if Session is not None and isinstance(Session, int) is False:
                Session = id(Session)

            exclude_list = Exclude.copy()
            exclude_list.append('C88')
            cfailures = cls.GetFailures(Session, Reset)
            cfailures = [cf for cf in cfailures if cf[1] not in exclude_list]
            if len(cfailures)==len(Failures):
                test = True
                for x in range(len(Failures)):
                    if cfailures[x][1]==Failures[x] is False:
                        test = False
        except Exception as e:
            test = False

        return test
