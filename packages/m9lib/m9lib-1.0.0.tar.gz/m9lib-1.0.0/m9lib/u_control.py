# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

from m9ini import uConfig, uConfigSection, uConfigParameters

from .u_dictionary import *
from .u_command import *
from .u_logger import *
from .u_timer import *
from .u_format import *

import datetime, os

# Configuration parameters:
# [<control-name>]
# Logfile = <log file full path with optional format entries {YMD}, {TSM}>
# Preview = <True|False> : when True, sets preview mode for commands
# Execute = A comma delimited list of command ids and/or group ids
# [Group:<id>]
# <id> = Section id
# Execute = a comma delimited list of command ids
# [Command:<id>]
# <id> = Command id for execute command

# Execution list rules:
# - An id of a command (a section that has a corresponding command registration)
# - An id of a group (a section that doesn't have a command registration, and has an Execute property)
# - A command name (has a corresponding registration); all groups with matching names are processed

class uControl:
    
    def __init__(self, Name, Config:str|uConfig, Params:list|uConfigParameters=None):
        '''
        - **Name**: control section name within configuration
        - **Config**: a **uConfig** or path to a configuration file
        - **Params**: optional configuration overrides, when **Config** is a path to a file (ignored otherwise)

        Control features are driven by configuration control section entries.

        ```
        [Name]
        Logfile = Path to log file; Recommended use of {YMD}, {TSM}
        Preview = True|False; when True, a preview flag is sent to commands
        Execute = Comma-delimited list of section ids, section names, and/or group ids
        ```
        '''
        self.now = datetime.datetime.now()
        self.name = Name
        self.config = None
        self.missing_config_file = None
        self.logger = None
        self.is_preview = False
        self.timer = None
        
        if isinstance(Config, uConfig):
            self.config = Config
        elif isinstance(Config, str):
            if os.path.isfile(Config):
                self.config = uConfig(Config, Params)
            else:
                self.missing_config_file = Config

        if self.config is not None:
            self.is_preview = self.config.GetSectionBool (self.name, "Preview") is True
            logfile = self.config.GetSectionValue(self.name, "Logfile")
            if logfile is not None:
                logfile = uStringFormat.String(logfile, Now=self.now)
                self.logger = uFileLogger(logfile)

        if self.logger is None:
            self.logger = uLogger()

        if self.config:
            failures = self.config.GetFailures(False)
            for failure in failures:
                self.logger.WriteWarning(failure)

        self.__init_results()

    def GetConfig (self):
        return self.config

    def GetControlName (self):
        '''
        Returns control name passed into the constructor.
        '''
        return self.name

    def GetControlConfig (self)->uConfigSection:
        '''
        Returns a configuration section based on the control name.
        '''
        return self.config.GetSection(self.name)
    
    def GetLogger (self)->uLogger:
        return self.logger
    
    def IsPreview (self):
        return self.is_preview

    def GetNow (self):
        '''
        Returns the time of instantiation.
        '''
        return self.now

    # failure system
    
    @classmethod
    def PrintFailures(cls, Print:bool=True, PrintColor:bool=True):
        '''
        Failures will be printed to the console.

        This includes system errors and errors logged from commands.  This does not include unsuccessful command results.
        '''
        uFailures.PrintFailures(Print, PrintColor)
        uConfig.PrintFailures(Print, PrintColor)
   
    def ClearFailures(self) -> bool:
        '''
        Clears the failure queue.
        '''
        return uFailures.ClearFailures(self)
    
    def HasFailures(self) -> bool:
        '''
        Returns *True* when there are failures available in **GetFailures()**.

        Failures include system errors and errors logged from commands.  This does not include unsuccessful command results.
        '''
        return uFailures.HasFailures(self)
    
    def GetFailures(self, Reset=True) -> list:
        '''
        Returns failures as a list of (code,context,message).

        If **Reset** is *True*, the internal failure list will clear.

        Failures include system errors and errors logged from commands.  This does not include unsuccessful command results.
        '''
        return uFailures.GetFailures(self, Reset)
    
    def __add_failure(self, code, message):
        uFailures.AddFailure(self, self, code, message)
        if self.logger:
            self.logger.WriteError (f"[{code}] {message}")
    
    # result helpers

    def GetFinalResult (self):
        '''
        The final result is the return value from imp_finalize().
        If imp_finalize() is not implemented, returns True when all commands were successful.
        '''
        return self.final_result
    
    def GetDuration (self):
        return self.timer.GetElapsedSeconds() if self.timer is not None else None
    
    def CountTotalErrors (self, Name=None, Id=None, Label=None):
        '''
        Returns the number of errors from specified sections.
        '''
        errors = 0
        results = self.GetResults (Name, Id, Label)
        for result in results:
            errors += result.CountErrors()

        return errors
    
    def GetResult (self, Id):
        '''
        Returns the first matching command result, or None if there are no results.

        **Id**: one of *name*, *id*, or *name*:*id*

        A command only has a result if it ran and was successful or a failure.  Skipped commands do not have results.
        '''
        if isinstance(Id, str) is False:
            return None

        results = []        
        ids = Id.split(':')
        if len(ids)>=2:
            results = self.GetResults(Name=ids[0].strip(), Id=ids[1].strip())
        else:
            results = self.GetResults(Id=Id)
            if len(results)==0:
                results = self.GetResults(Name=Id)
        return results[0] if len(results)>0 else None
    
    def GetResults (self, Name=None, Id=None, Label=None, IsSuccess=None):
        '''
        Returns a list of matching command results.
        '''
        results = []
        for command in self.commands:
            if command['result'] is not None:
                if command['result'].IsMatch(Name, Id, Label):
                    if IsSuccess is None or IsSuccess is command['result'].IsSuccess():
                        results.append(command['result'])

        return results

    def GetSkipped (self):
        '''
        Returns a list of skipped commands without results as command names with id.
        '''
        skipped = []
        for command in self.commands:
            if command['result'] is None:
                comid = command['name']
                if isinstance(command['params'], uConfigSection):
                    if command['params'].GetId() is not None:
                        comid += f":{command['params'].GetId()}"
                skipped.append(comid)

        return skipped

    def CountSuccess (self, IsSuccess=True):
        '''
        Returns a count of matching command results based on success.
        Success of None means the command was not executed (skipped) due to creation or initialization issues.
        '''
        count = 0
        for command in self.commands:
            if command['result'] is None:
                if IsSuccess is None:
                    count += 1
            elif IsSuccess == command['result'].IsSuccess():
                count += 1

        return count
    
    def GetSummary (self)->dict:
        '''
        Returns a dict that summarizes the results of command execution.
        '''
        stats = {}
        stats['total_commands'] = len(self.commands)
        stats['total_warnings'] = 0
        stats['total_errors'] = 0
        stats['count_skipped'] = 0
        stats['count_success'] = 0
        stats['count_failure'] = 0
        stats['duration'] = self.GetDuration()
        stats['results'] = []

        for command in self.commands:
            result = {'command':command['name'],
                      'id':None,
                      'success':None,
                      'result':None,
                      'warnings':None,
                      'errors':None,
                      'duration':None}
            
            if command['result'] is None:
                stats['count_skipped'] += 1
                if isinstance(command['params'], uConfigSection):
                    result['id'] = command['params'].GetId()
            else:
                result['id'] = command['result'].GetCommandId()
                result['success'] = command['result'].IsSuccess()
                result['result'] = command['result'].GetResult()
                result['warnings'] = command['result'].CountWarnings()
                result['errors'] = command['result'].CountErrors()
                result['duration'] = command['result'].GetDuration()
                stats['total_warnings'] += result['warnings']
                stats['total_errors'] += result['errors']
                stats['duration'] = command['result'].GetDuration()
                if result['success']:
                    stats['count_success'] += 1
                else:
                    stats['count_failure'] += 1
            
            stats['results'].append(result)

        return stats

    # command execution

    def Execute (self, ExeList=None):
        '''
        Executes a batch of commands.

        If ExeList is None, loads a list of command targets from "Execute" in the command section.
        Otherwise, ExeList can be a comma delimited string, or a list of strings.

        Entries in ExeList can be:
        - a configuration section, by id (section name must match a registered command)
        - a command name (will execute all sections with a matching name)
        - a configuration section named "Group", by id containing an "Execute" list.
        '''

        ret = self.__pre_execute()
        if ret is not True:
            return ret
        
        self.__build_command_list (ExeList)

        return self.__post_execute()

    def ExecuteCommand (self, CommandName, CommandTarget):
        '''
        Execute a single command.

        **CommandName** is the name of a registered class.

        **CommandTarget** indicates where to find execution parameters:
        - *None*: looks for a section by class name in configuration
        - *Id*: looks for a section by class name and id in configuration
        - **dict** or **uDictionary**: used as explicit parameters
        - **uConfigSection**: use specified section values        
        '''

        ret = self.__pre_execute()
        if ret is not True:
            return ret
        
        if CommandName is None and isinstance(CommandTarget, uConfigSection):
            CommandName = CommandTarget.GetClass()
        
        self.__add_command(CommandName, CommandTarget)

        return self.__post_execute()
    
    # override methods
        
    def imp_ini_command (self, in_command):
        '''
        Called to perform additional command initialization before execution.
        
        Return the following:
        - *True*: successfully performed initialization -- execute command
        - *False*: initialization failed -- do not execute command
        - *None*: initialization was not required -- execute command
        '''
        return None

    def imp_prepare (self):
        '''
        Called before processing any commands.

        Return *False* to fail the entire process.
        '''
        return None
    
    def imp_finalize (self):
        '''
        Called after processing commands.

        Return a result code or string that will be returned by GetFinalResult().

        If *None* is returned, GetFinalResult() returns *True* when all commands were successful, and at least one command was executed.
        '''
        return None
    
    # internal command processing
    
    def __init_results (self):
        self.commands = []
        self.final_result = None
    
    def __add_command (self, in_name:str, in_params):
        # check for duplicate section
        com_class = in_name
        if isinstance(in_params, uConfigSection):
            for command in self.commands:
                if command['params'] is in_params:
                    return False
            com_class = in_params.GetClass()
        elif isinstance(in_params, dict):
            if '*name' not in in_params:
                in_params['*name'] = com_class
        elif isinstance(in_params, uDictionary):
            if in_params.HasValue('*name') is False:
                in_params.SetValue('*name', com_class)
            
        self.commands.append({'name':in_name, 'params':in_params, 'class':com_class, 'result':None})
        return True
        
    def __pre_execute (self):
        self.__init_results ()
        
        if self.config is None:
            if self.missing_config_file:
                self.__add_failure("C01", f"No control configuration (config file not found): {self.missing_config_file}")
            else:
                self.__add_failure("C01", "No control configuration")
            return None

        pstr = ""
        if self.IsPreview ():
            pstr = " [Preview]"

        self.logger.WriteLine ("[+BLUE]" + "=" * 69 + "[+]")
        self.logger.WriteLine ("[+BLUE]===[+][+CYAN] " + self.name+pstr + "[+]")
        self.logger.WriteLine ("[+BLUE]" + "=" * 69 + "[+]")
        
        self.timer = uTimer()

        if self.imp_prepare () is False:
            self.logger.WriteError ("C02", "Failed preparation step")
            return False
        
        return True

    def __post_execute (self):
        for command in self.commands:
            com = self.__new_command(command['class'], command['params'])
            if com is not None:
                command['result'] = com.Execute (Target=False, Preview=self.IsPreview ())

        self.logger.WriteLine ("[+BLUE]" + "=" * 69 + "[+]")

        self.final_result = self.imp_finalize()
        if self.final_result is None:
            if len(self.commands)>0:
                self.final_result = (self.CountSuccess()==len(self.commands))

        self.timer.Stop()

        fstr = ""
        if isinstance(self.final_result, str):
            fstr.format("{fr} ", fr=self.final_result)
        
        self.logger.WriteLine ("=== {fr}({f})".format(fr=fstr,f=self.timer.GetElapsedString()))
        self.logger.WriteBlank()

        return self.final_result
    
    # internal methods

    def __find_command_sections (self, in_id, in_process_groups=True):
        # helper to return matching command sections based on id
        # if the section name is "Group", this will be expanded unless in_process_groups is False (to prevent recursion)
        # supports $ starts with
        # execution paramters are a list of any:
        #   - command id (by id)
        #   - execution group (name of "Group", by id)
        #   - command name (by name)
        # returns a list of uConfigSection
        slist = []

        # is this a command?  search by name
        if uCommandRegistry.IsCommand(in_id):
            sections = self.config.GetSections(Name=in_id)
            if len(sections)==0:
                self.__add_failure("C03", "No command sections found by name: "+in_id)
            return sections

        # search for sections by name
        sections = self.config.GetSections(Name=in_id)

        # search for sections by id
        sections.extend(self.config.GetSections(Id=in_id))
        if len(sections)==0:
            self.__add_failure("C04", "No command sections found by id: "+in_id)

        for section in sections:
            if section.GetName () == "Group":
                if in_process_groups:
                    glist = section.GetList ("Execute")
                    if glist is None or len(glist)==0:
                        self.__add_failure("C05", "No group execute list specified for section with id: "+in_id)
                    else:
                        self.GetLogger().WriteLine("Group Execute (" + in_id + ") = " +  ",".join (glist))
                        for g in glist:
                            gsection = self.__find_command_sections(g, False)
                            # if len(gsection)==0:
                            #     self.__add_failure("C06", "Failed to find Execute section with id: "+g)
                            slist.extend(gsection)
            else:
                if uCommandRegistry.IsCommand(section.GetClass()):
                    slist.append(section)
                else:
                    self.__add_failure("C07", f"Unknown command: {section.GetClass()} [{section.GetSpecification()}]")

        return slist
    
    def __build_command_list (self, in_execute=None):
        # based on execution parameters, builds a command list with proper configuration
        # if in_execute is specified, no need to check for Execute setting, can be a string or list of strings
        exelist = None
        if isinstance(in_execute, list):
            exelist = in_execute
        elif isinstance(in_execute, str):
            exelist = uStringFormat.Strip(in_execute.split(','))
        else:
            control_section = self.config.GetSection(self.name)
            if control_section is None:
                self.__add_failure("C01", f"No control configuration (control section not found): [{self.name}]")
                return
            exelist = control_section.GetList("Execute")

        if exelist is None or len(exelist)==0:
            self.__add_failure("C10", f"No Execute list specified: [{self.name}].Execute is empty")
        else:
            self.GetLogger().WriteLine("Execute = " + ",".join(exelist))
            for exe in exelist:
                sections = self.__find_command_sections(exe)
                for section in sections:
                    self.__add_command(section.GetName(), section)
        pass
    
    def __new_command (self, in_name, in_params:uConfigSection):
        com = uCommandRegistry.NewCommand (in_name)
        if com:
            com.SetControl(self)
            com.SetConfig(self.config)
            com.SetLogger(self.logger)
            com.SetParams(in_params)
            ret = self.imp_ini_command(com)
            if ret is False:
                self.__add_failure("C09", "Failed command initialization for " + str(in_name))
                return None
        else:
            self.__add_failure("C08", "Unable to build command class " + str(in_name))
        return com
