# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

import datetime
from .u_format import *

class uTimer:
    
    def __init__(self):
        '''
        Timer is started automatically.
        '''
        self.Start()
        
    def Start (self):
        '''
        Restarts the timer.
        '''
        # restarts, clearing all values
        self.start = datetime.datetime.now()
        self.stop = None
        
    def Stop (self):
        '''
        Stops the timer.
        '''
        self.stop = datetime.datetime.now()
        
    def GetElapsedSeconds (self)->float:
        '''
        Returns elapsed duration in seconds as a decimal number.
        '''
        stop = self.stop
        if stop is None:
            stop = datetime.datetime.now()
        delta = stop - self.start
        return delta.total_seconds()
    
    def GetElapsedString (self, Units=None)->str:
        '''
        Returns elapsed seconds as a string, using uStringFormat.Duration().

        **Units** is one of: "d", "h", "m", "s", or *None*.

        If **Units** is *None*, units will be selected automatically.
        '''
        return uStringFormat.Duration (self.GetElapsedSeconds (), Units)
