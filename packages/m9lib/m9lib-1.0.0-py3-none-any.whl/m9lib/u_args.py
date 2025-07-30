# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

import re, sys

# Argument format follows:
#   - Some number of options and parameters:
#   - An option may be configured to expect a value:
#       -<option>
#       -<option>:<optparam>
#       -<option> <optparam>
#   - A string that is not preceded by a dash and does not follow an option that expects a value is an argument param

class uArgs:
    def __init__(self, Options:list=None, Params:list=None) -> None:
        self.options = {}
        self.params = []
        self.parsed_options = None
        self.parsed_params = None
        self.bad_options = None
        self.bad_params = None
        self.missing_options = None

        if isinstance(Options, list):
            # in_options is a list of (name, short, hasvalue)
            for option in Options:
                if isinstance(option, str):
                    self.AddOption(option)
                elif isinstance(option, tuple):
                    short = None
                    hasvalue = False
                    if len(option)>2:
                        hasvalue = bool(option[2])
                    self.AddOption(option[0], option[1], hasvalue)

        if isinstance(Params, list):
            for param in Params:
                self.AddParam(param)

    def AddOption(self, Option:str, Short:str=None, HasValue:bool=False):
        '''
        Adds a named option.
        - **Option**: the option name
        - **Short**: a short version of the option name
        - **HasValue**: the option is expected to have an option value

        An option is specified as *-option* using the option name.

        When **HasValue** is True, an option can be specified as *-option value* or *-option:value*.
        '''
        self.options[Option] = {'option': Option, 'short': Short, 'hasvalue': HasValue}

    def AddParam(self, Param:str):
        '''
        Adds a named parameter.
        - **Param**: the parameter name
        
        Parameters are matched in sequential order.
        '''
        self.params.append(Param)

    def Parse(self, Args=None):
        '''
        **Args** can be a list of strings or a string with space delimited arguments.

        If *None* is specified, arguments come from *sys.argv* (removing first entry).

        It is not necessary to call Parse() when using system arguments, as this is the default.
        '''
        if isinstance(Args, str):
            Args = self.__parse_arguments(Args)

        if Args is None:
            Args = sys.argv [1:]

        if isinstance(Args, list) is False:
            return False
        
        # clean up arguments by stripping whitespace
        Args = [s.strip() for s in Args if s.strip()!='']

        self.parsed_options = {}
        self.parsed_params = {}
        self.bad_options = None
        self.bad_params = None
        self.missing_options = None
        curoption = None
        for arg in Args:
            if arg.startswith("-"):
                while len(arg)>0 and arg[0]=='-':
                    arg = arg [1:]
                if len(arg)>0:
                    if curoption is not None:
                        self.__missing_option(curoption)

                    curoption = self.__find_option(arg)
                    if curoption:
                        if self.options[curoption]['hasvalue'] is False:
                            self.parsed_options[curoption] = True
                            curoption = None
                    else:
                        csplit = arg.split(':', 1)
                        if len(csplit)>1:
                            curoption = self.__find_option(csplit[0])
                            if curoption:
                                if self.options[curoption]['hasvalue'] is True:
                                    self.parsed_options[curoption] = csplit[1]
                                elif csplit[1].lower().startswith('t'):
                                    self.parsed_options[curoption] = True
                                else:
                                    self.parsed_options[curoption] = False
                                curoption = None
                            else:
                                self.__bad_option(arg)
                        else:
                            self.__bad_option(arg)
            elif curoption:
                self.parsed_options[curoption] = arg
                curoption = None
            else:
                cnt = len(self.parsed_params.keys())
                if cnt < len(self.params):
                    self.parsed_params[self.params[cnt]]=arg
                else:
                    self.__bad_param(arg)

        if curoption is not None:
            self.__missing_option(curoption)

        return True
    
    def NoArguments(self):
        '''
        Returns *True* when no arguments were specified.
        '''
        self.__check_parse()
        return len(list(self.parsed_options.keys())) + len(list(self.parsed_params.keys())) == 0

    def HasOption(self, Option:str):
        '''
        **Option** can be the natural or short form of the option.

        Returns *True* if an option was provided in arguments.
        '''
        self.__check_parse()
        Option = self.__find_option(Option)
        if Option in self.options:
            if (Option in self.parsed_options):
                return True
        return False

    def GetOption(self, Option:str):
        '''
        **Option** can be the natural or short form of the option.

        If the option expects a value, the provided value is returned.

        Returns *None* if option not specified
        '''
        self.__check_parse()
        Option = self.__find_option(Option)
        if Option in self.options:
            if Option in self.parsed_options:
                return self.parsed_options[Option]
            return None
        return False
    
    def HasParam(self, Param:str):
        '''
        Returns *True* if a parameter was configured and provided in the arguments.
        '''
        self.__check_parse()
        if Param in self.params:
            return (Param in self.parsed_params)
        return False

    def GetParam(self, Param:str):
        '''
        Returns the parameter value, or None if the parameter was not provided.

        Returns *False* if the parameter was not configured.
        '''
        self.__check_parse()
        if Param in self.params:
            if Param in self.parsed_params:
                return self.parsed_params[Param]
            return None
        return False
    
    def GetBadOptions(self):
        '''
        Returns a list of options that were provided but not configured, or *None* if there are no bad options.
        '''
        return self.bad_options

    def GetBadParams(self):
        '''
        Returns a list of parameters that were provided but not configured, or *None* if there are no bad parameters.
        '''
        return self.bad_params
    
    def GetMissingOptions(self):
        '''
        Returns a list of options that were provided without value options.

        These options are valid options, but configured to expect an option value.
        '''
        return self.missing_options

    # Internal methods
    
    def __parse_arguments(self, in_args):
        pattern = r'(?:"([^"]*)"|(\S+))'
        matches = re.findall(pattern, in_args)
        result = [match[0] or match[1] for match in matches if match[0] or match[1]]
        return [arg.strip() for arg in result if arg.strip()]      

    def __check_parse(self):
        if self.parsed_options is None:
            self.Parse()

    def __find_option(self, in_option):
        if in_option in self.options:
            return in_option
        optkeys = list(self.options.keys())
        for option in optkeys:
            if self.options[option]['short']==in_option:
                return option
        return None
    
    def __bad_option(self, in_option):
        if self.bad_options is None:
            self.bad_options = []
        self.bad_options.append(in_option)

    def __bad_param(self, in_param):
        if self.bad_params is None:
            self.bad_params = []
        self.bad_params.append(in_param)

    def __missing_option(self, in_option):
        if self.missing_options is None:
            self.missing_options = []
        self.missing_options.append(in_option)
