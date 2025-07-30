# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

from m9ini import uConfig, uConfigSection, uSectionHeader

from .u_logger import *
from .u_timer import *
from .u_dictionary import *
from .u_failures import uFailures

class uCommandException(Exception):
    def __init__(self, in_code, in_message):
        self.code = in_code
        self.message = f"{in_message}"
        super().__init__(self.message)

class uCommandResult:
    # Represents a command result
    # Results should be: "Success", "Failure"
    # There can still be errors
    def __init__(self):
        self.result = None
        self.timer = None
        self.messages = []
        self.warn_count = 0
        self.error_count = 0
        self.command = None
        self.section_header = None
        
    def GetSectionName(self)->str:
        return self.section_header.GetName()
    
    def GetCommandId(self)->str:
        return self.section_header.GetId()
    
    def GetCommandClass(self)->str:
        return self.section_header.GetClass()
        
    def GetResultClass(self)->str:
        return self.__class__.__name__
    
    def GetSpecification(self):
        '''
        Returns the section header specification.
        '''
        return self.section_header.GetSpecification()

    def SetHeader(self, Command, Header:uSectionHeader):
        self.command=Command
        self.section_header = Header

    def SetResult(self, Result):
        '''
        **Result** should be *True* or "Success" if command execution was successful.
        
        Otherwise, set a failure string.
        '''
        if Result==True or (isinstance(Result, str) and Result.lower()=="success"):
            Result = "Success"
        self.result = Result
        
    def GetResult(self)->str:
        return self.result
    
    def IsSuccess(self)->bool:
        '''
        Returns True if the result was "Success".
        '''
        return self.result=="Success"
    
    def GetDuration(self)->float:
        '''
        Gets the duration of the command in seconds.
        '''
        return self.timer.GetElapsedSeconds() if self.timer is not None else None
    
    def IsMatch (self, Name=None, Id=None, Label=None)->bool:
        '''
        Returns *True* when the source parameters for the associated command matches specified criteria.

        Critiera starting with $ means "starts with".
        '''
        if self.section_header is not None:
            return self.section_header.IsMatch(Name, Id, Label)
        return False
    
    def GetMessages(self, Level:uLoggerLevel=None)->list:
        '''
        Returns a list of (Level, Message).

        If **Level** is specified, list contains messages at or above the specified level.
        '''
        if Level is None:
            return self.messages

        return [message for message in self.messages if message[0]>=Level]
    
    def AddMessage(self, Level:uLoggerLevel, Message:str):
        '''
        Adds a message to the command result.

        Logged messages will be added to the command result automatically.  Use this method to add a message to results without logging the message.

        ERROR level messages will be added to the **uControl** failure queue.
        '''
        if Level==uLoggerLevel.WARNING:
            self.warn_count += 1
        elif Level>=uLoggerLevel.ERROR:
            self.error_count += 1
            session = self.command.GetControl() if isinstance(self.command, uCommand) else self.command
            context = self.section_header.GetSpecification() if isinstance(self.section_header, uSectionHeader) else self.__class__.__name__
            uFailures.AddFailure(session, context, "C88", Message)

        self.messages.append((Level, Message))
        
    def CountWarnings(self)->int:
        '''
        Returns a count of warning messages.
        '''
        return self.warn_count
    
    def CountErrors(self)->int:
        '''
        Returns a count of error messages.
        '''
        return self.error_count

class uCommandRegistry():

    _registry = {}

    @classmethod
    def RegisterCommand(cls, CommandClass, ResultClass=None)->bool:
        '''
        Register a command class.  **CommandClass** must be derived from **uCommand**.

        If **ResultClass** is not specified, **uCommandResult** will be used.
        '''
        ClassName = CommandClass.__name__
        cls._registry[ClassName] = {'funcNewCommand': CommandClass, 'funcNewResult': ResultClass}
        return True

    @classmethod
    def NewCommand(cls, ClassName:str):
        '''
        Constructs a new command object of a registered command class.
        '''
        if ClassName in cls._registry and cls._registry[ClassName]['funcNewCommand'] is not None:
            return cls._registry[ClassName]['funcNewCommand']()
        return None
            
    @classmethod
    def NewResult(cls, ClassName:str)->uCommandResult:
        '''
        Constructs a new result object of a registered command class.
        '''
        if ClassName in cls._registry and cls._registry[ClassName]['funcNewResult'] is not None:
            return cls._registry[ClassName]['funcNewResult']()
        return uCommandResult()
    
    @classmethod
    def IsCommand(cls, ClassName)->bool:
        '''
        Returns *True* if **ClassName** is a registered command class.
        '''
        return ClassName in cls._registry

class uCommand:

    re_paramstring = None
    
    def __init__(self):
        self.config = None
        self.defaults = None
        self.params = None
        self.logger = None
        self.ispreview = False
        self.result = None
        self.control = None

    # Setup

    def SetConfig(self, Config:uConfig|str):
        '''
        Sets configuration for the command.  Takes either a **uConfig** object, or a path to a configuration file.

        Not required.  Parameters will come from the Execute() call.
        '''
        if isinstance(Config, uConfig):
            self.config = Config
        elif isinstance(Config, str):
            self.config = uConfig(Config)

    def SetLogger(self, Logger:uLogger):
        '''
        Provides a logger for the command.  Takes either a **uLogger** object, or a path to a log file.  Log enties will be appended to the file.

        Not required.  If not specified, a console logger will be used which prints warnings and errors.
        '''
        if isinstance(Logger, uLogger):
            self.logger = Logger
        elif isinstance(Logger, str):
            self.logger = uFileLogger(Logger)

    def SetControl(self, Control):
        '''
        Called by **uControl**.
        '''
        self.control = Control
        if Control is not None:
            self.SetConfig(Control.GetConfig())
            self.SetLogger(Control.GetLogger())

    def SetParams(self, Params:uConfigSection|dict|uDictionary):
        '''
        Set command parameters.
        '''
        if self.params is None:
            self.params = Params

    def GetConfig(self)->uConfig:
        return self.config

    def GetLogger(self)->uLogger:
        return self.logger
    
    def GetControl(self):
        return self.control
        
    def IsPreview(self)->bool:
        return self.ispreview
    
    def SetDefaults(self, Defaults:list=None):
        '''
        Called by command initialization to set defaults for command parameters.  These are applied last.

        Expects a list of (*name*, *value*).
        '''
        self.defaults = None
        if isinstance(Defaults, tuple):
            Defaults = [Defaults]
        if isinstance(Defaults, list):
            for entry in Defaults:
                if isinstance(entry, tuple):
                    if isinstance(entry[0],str) and entry[1] is not None:
                        if self.defaults is None:
                            self.defaults = {}
                        self.defaults[entry[0]] = str(entry[1])
    
    # Identification

    def GetClass(self)->str:
        '''
        Returns the command class for the command.
        '''
        # Command class
        return self.__class__.__name__
    
    def GetName (self)->str:
        '''
        When parameters is a **uConfigSection**, gets the command name from the configuration section header.

        Otherwise, name comes from a dictionary "*name" entry.
        '''
        if isinstance(self.params, uConfigSection):
            return self.params.GetName ()
        return self.GetParam("*name")

    def GetId (self)->str:
        '''
        When parameters is a **uConfigSection**, gets the command id from the configuration section header.

        Otherwise, id comes from the "*id" entry.
        '''
        if isinstance(self.params, uConfigSection):
            return self.params.GetId ()
        return self.GetParam("*id")
    
    # Parameter access

    def HasParam(self, Param):
        return self.__has_value(Param)

    def GetParam(self, Param, Default=None):
        v = self.__get_value(Param)
        return v if v is not None else Default

    def GetIntParam(self, Param, Default=None):
        v = self.__get_number(Param)
        return v if v is not None else Default

    def GetFloatParam(self, Param, Default=None):
        v = self.__get_float(Param)
        return v if v is not None else Default

    def GetBoolParam(self, Param, Default=None):
        v = self.__get_bool(Param)
        return v if v is not None else Default

    def GetListParam(self, Param, Default=None):
        v = self.__get_list(Param)
        return v if v is not None else Default
    
    # Parameter helpers

    def __has_default(self, in_param):
        return self.defaults is not None and in_param in self.defaults

    def __get_default(self, in_param):
        return self.defaults[in_param] if self.__has_default(in_param) else None

    def __has_value(self, in_param):
        if isinstance(self.params, uConfigSection):
            return self.params.HasValue(in_param) or self.__has_default(in_param)
        elif isinstance(self.params, uDictionary):
            return self.params.HasValue(in_param) or self.__has_default(in_param)
        elif isinstance(self.params, dict):
            return (in_param in self.params) or self.__has_default(in_param)
        return False

    def __get_value(self, in_param):
        if isinstance(self.params, uConfigSection):
            return self.params.GetValue(in_param, Default=self.__get_default(in_param))
        elif isinstance(self.params, uDictionary):
            return self.params.GetValue(in_param, Default=self.__get_default(in_param))
        elif isinstance(self.params, dict):
            return self.params[in_param] if in_param in self.params else self.__get_default(in_param)
        return None

    def __get_number(self, in_param):
        if isinstance(self.params, uConfigSection):
            return self.params.GetNumber(in_param, self.__get_default(in_param))
        elif isinstance(self.params, uDictionary):
            return self.params.GetNumber(in_param, self.__get_default(in_param))
        elif isinstance(self.params, dict):
            if in_param in self.params:
                return uType.ConvertToInt(self.params[in_param])
            else:
                return uType.ConvertToInt(self.__get_default(in_param))
        return None

    def __get_float(self, in_param):
        if isinstance(self.params, uConfigSection):
            return self.params.GetFloat(in_param, self.__get_default(in_param))
        elif isinstance(self.params, uDictionary):
            return self.params.GetFloat(in_param, self.__get_default(in_param))
        elif isinstance(self.params, dict):
            if in_param in self.params:
                return uType.ConvertToFloat(self.params[in_param])
            else:
                return uType.ConvertToFloat(self.__get_default(in_param))
        return None

    def __get_bool(self, in_param):
        if isinstance(self.params, uConfigSection):
            return self.params.GetBool(in_param, self.__get_default(in_param))
        elif isinstance(self.params, uDictionary):
            return self.params.GetBool(in_param, self.__get_default(in_param))
        elif isinstance(self.params, dict):
            if in_param in self.params:
                return uType.ConvertToBool(self.params[in_param])
            else:
                return uType.ConvertToBool(self.__get_default(in_param))
        return None

    def __get_list(self, in_param, in_separator=","):
        if isinstance(self.params, uConfigSection):
            return self.params.GetList(in_param, in_separator)
        elif isinstance(self.params, uDictionary):
            return self.params.GetList(in_param, in_separator)
        elif isinstance(self.params, dict):
            if in_param in self.params:
                return uType.ConvertToList(self.params[in_param], in_separator)
        return None

    def IsMatch (self, Name=None, Id=None, Label=None)->bool:
        '''
        Returns *True* when the command matches specified criteria.
        '''
        if isinstance(self.params, uConfigSection):
            return self.params.IsMatch (Name, Id, Label)

        if Name is not None:
            return Name == self.GetName()

        return (Id is None and Label is None)

    def GetResult(self)->uCommandResult:
        '''
        Returns a **uCommandResult** or derived object containing command results.

        Returns *None* if the command hasn't run or failed initialization.
        '''
        return self.result

    def IsSuccess(self):
        '''
        Returns *True* if command execution returned "Success".

        Returns *None* if the command hasn't been executed.
        '''
        return self.result.GetResult()=="Success" if self.result is not None else None
    
    def Execute(self, Target=None, Preview=False)->uCommandResult:
        '''
        Executes the command.

        **Target** indicates where to find execution parameters:
        - *None*: looks for a section by class name in configuration
        - *Id*: looks for a section by class name and id in configuration
        - **dict** or **uDictionary**: used as explicit parameters
        - **uConfigSection**: use specified section values

        If multiple sections are found or no sections are found, execution will fail.

        Section class must match command class when using **uConfigSection**.

        Returns a **uCommandResult**.
        '''

        self.result = None

        try:
            exception_message = None
            if Target is False:
                # params was set by uControl in advance
                pass
            else:
                self.params = None
                if self.config and (Target is None or isinstance(Target, str)):
                    classname = self.GetClass()
                    sectionstr = classname if Target is None else f"{classname}:{Target}"
                    sections = self.config.GetSections(Name=classname, Id=Target)

                    if len(sections)==0:
                        raise uCommandException("C21", f"Command execution failed: section not found ({sectionstr})")
                    elif len(sections)>1:
                        raise uCommandException("C22", f"Command execution failed: multiple matching sections ({sectionstr})")

                    self.params = sections[0]
                elif isinstance(Target, uConfigSection):
                    if self.GetClass() != Target.GetClass():
                        raise uCommandException("C23", f"Command execution failed: command class mismatch ({Target.GetClass()})")
                    self.params = Target
                elif isinstance(Target, uDictionary):
                    self.params = Target
                    if self.params.HasValue('*name') is False:
                        self.params.SetValue('*name', self.GetClass())
                elif isinstance(Target, dict):
                    self.params = uDictionary(Target)
                    if self.params.HasValue('*name') is False:
                        self.params.SetValue('*name', self.GetClass())
        except uCommandException as e:
            exception_message = (e.code, e.message)
        except Exception as e:
            exception_message = ("C99", str(e))

        if exception_message:
            header = self.params.GetHeader() if isinstance(self.params, uConfigSection) else uSectionHeader(self.GetClass())
            context = header.GetSpecification()
            uFailures.AddFailure(self.control, context, exception_message[0], exception_message[1])
            self.result = uCommandRegistry.NewResult(self.GetClass())
            errstr = "Failure identifying execution target"
            if self.result is not None:
                self.result.SetHeader(self, header)
                self.result.SetResult(errstr)
            print (f"> Result: {errstr}")
            return self.result

        namestr = uType.SafeString(self.GetName ())
        self.ispreview = Preview
        s2 = " [Preview]" if Preview else ""

        self.result = uCommandRegistry.NewResult(self.GetClass())
        if self.result is not None:
            if isinstance(self.params, uConfigSection):
                self.result.SetHeader(self, self.params.GetHeader())
            else:
                self.result.SetHeader(self, uSectionHeader(Name=self.GetName(), Class=self.GetClass(), Id=self.GetId()))

        idstr = "({i})".format(i=self.GetId ()) if self.GetId() is not None else ""
        self.LogMessage ("[+LT_VIOLET]" + "+" * 69 + "[+]")
        self.LogMessage ("[+LT_VIOLET]+++[+] " + "[+VIOLET]{n} {i}{s}[+]".format(n=namestr, i=idstr, s=s2))
        self.LogMessage ("[+LT_VIOLET]" + "+" * 69 + "[+]")
    
        self.result.timer = uTimer()
        ret = self.imp_execute(Preview)
        self.result.timer.Stop()
    
        fstring = self.result.timer.GetElapsedString()
        self.LogMessage ("+++ ({f})".format(f=fstring))
        self.result.SetResult(ret)
        print ("> Result: {r} ({f})".format(r=ret, f=fstring))
        return self.result
    
    # Parameterr logging
    
    def LogParam(self, Param, Value=None, IfNone:bool=True):
        '''
        Helper method for logging a parameter value.
        
        If **Value** is *None*, gets parameter value using GetParam() .

        If **IfNone** is False, skips logging if the value to print is *None*.
        '''
        if Value is None:
            Value = self.GetParam(Param)
        if Value is None:
            Value = ""
        if Value!="" or IfNone is True:
            self.LogMessage("[+BLUE]{p} = {v}[+]".format(p=Param, v=Value))

    def LogParams(self, ParamList:list, IfNone:bool=True):
        '''
        Logs a list of parameters.

        **ParamList** is a list strings or tuple where the second value is passed in as *Value*.
        '''
        if isinstance(ParamList, list):
            for p in ParamList:
                if isinstance(p, str):
                    self.LogParam(p, IfNone=IfNone)
                elif isinstance(p, tuple):
                    self.LogParam(p[0],p[1], IfNone=IfNone)

    def LogParamString(self, ParamString:str, ParamStringNone:str=None, IfNone:bool=True):
        '''
        Logs *ParamString* after replacing parameter values reprented as [=PARAM].

        If any of the the param values are *None*:
        - If *IfNone* is *False*, return without logging
        - If *ParamStringNone* is not *None*, use this string instead of *ParamString*
        '''
        re_paramstring = uCommand.__re_paramstring()
        m = re_paramstring.findall(ParamString)
        if len(m)==0:
            self.LogMessage(f"[+BLUE]{ParamString}[+]")
            return
        
        anynone = False
        mvals = {}
        for p in m:
            mvals[p] = self.GetParam(p)
            if mvals[p] is None:
                anynone = True

        if anynone:
            if IfNone is False:
                return

            if ParamStringNone is not None:
                ParamString = ParamStringNone

        for p in m:
            ParamString = ParamString.replace(f"[={p}]", f"{mvals[p]}")
        
        self.LogMessage(f"[+BLUE]{ParamString}[+]")

    def LogParamStrings(self, ParamStringList:list, IfNone:bool=True):
        '''
        Logs a list of param strings using **LogParamString()**.

        List can contain a combination of strings and tuples where the second value is passed as *ParamStringNone*.
        '''
        if isinstance(ParamStringList, list):
            for pstr in ParamStringList:
                if isinstance(pstr, str):
                    self.LogParamString(pstr, IfNone=IfNone)
                if isinstance(pstr, tuple):
                    self.LogParamString(pstr[0], pstr[1], IfNone=IfNone)

    @classmethod
    def __re_paramstring(cls):
        if cls.re_paramstring is None:
            cls.re_paramstring = re.compile(r'\[\=(\w+)?\]')
        return cls.re_paramstring
    
    # Message logging

    def LogDetails(self, Message):
        if self.logger is not None:
            self.logger.WriteDetails(Message)
        self.result.AddMessage(uLoggerLevel.DETAILS, uConsoleColor.Format(Message, StripColors=True))
        
    def LogMessage(self, Message):
        if self.logger is not None:
            self.logger.WriteLine(Message)
        self.result.AddMessage(uLoggerLevel.INFO, uConsoleColor.Format(Message, StripColors=True))
        
    def LogWarning(self, Message):
        if self.logger is not None:
            self.logger.WriteWarning(Message)
        if self.result is not None:
            self.result.AddMessage(uLoggerLevel.WARNING, uConsoleColor.Format(Message, StripColors=True))
        
    def LogError(self, Message):
        if self.logger is not None:
            self.logger.WriteError(Message)
        if self.result is not None:
            self.result.AddMessage(uLoggerLevel.ERROR, uConsoleColor.Format(Message, StripColors=True))
            
    # Subclass implementation
        
    def imp_execute(self, in_preview):
        '''
        Implement this method in your **uCommand**-derived class.

        Perform execution and return "Success", *True*, or a failure string.
        '''
        self.LogMessage ("imp_execute not implemented")
        return "Not implemented"
