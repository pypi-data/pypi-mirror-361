# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

import threading

class CriticalSectionCounter:
    def __init__(self):
        self.counter = 0
        self.max = 0
        self.lock = threading.Lock()

    def enter_critical_section(self):
        with self.lock:
            if self.counter==0:
                self.max = 0
                # print(f"Entered critical section")
            self.counter += 1
            self.max = max(self.counter, self.max)
            # print(f"Entered critical section, count: {self.counter}")

    def exit_critical_section(self):
        with self.lock:
            self.counter -= 1
            # print(f"Exited critical section, count: {self.counter}")
            # if self.counter==0:
            #     print(f"Exited critical section; max: {self.max}")

    def get_count(self):
         with self.lock:
            return self.counter

class ConfigSectionLock(CriticalSectionCounter):
    def __init__(self):
        super().__init__()
        self.__reset()

    def Lock(self, in_section, in_property):
        if self.get_count()==9:
            return False
        
        self.enter_critical_section()
        if self.get_count()==1:
            self.__reset()
            self.section = in_section
            self.section_name = f"[{in_section.GetSpecification()}]"
            self.property_name = in_property
            pass
        return True
        
    def Unlock(self, Return, GetValueHash=None):
        self.exit_critical_section()
        if GetValueHash:
            self.PopGetValue(GetValueHash)

        return Return
    
    # Lock state
    
    def LastError(self) -> str:
        return self.last_error
    
    def RecursionError(self) -> bool:
        return self.last_error in ["E19", "E20"]
    
    def SetLastError(self, LastError):
        self.last_error = LastError

    def PushGetValue(self, GetValueHash) -> bool:
        if GetValueHash in self.getvalue_queue:
            return False
        
        self.getvalue_queue.append(GetValueHash)
        
    def PopGetValue(self, GetValueHash):
        if GetValueHash in self.getvalue_queue:
            self.getvalue_queue.remove(GetValueHash)

    # Original section / property

    def TestSection(self, in_section):
        return (self.section==in_section)

    def GetSectionName(self):
        return self.section_name

    def GetPropertyName(self):
        return self.property_name
    
    # Description queue

    def GetDescription(self):
        if len(self.desc_override)>0:
            return self.desc_override[-1]
        return self.desc_queue[-1] if len(self.desc_queue)>0 else ""
    
    def PushDescription(self, in_desc):
        self.desc_queue.append(in_desc)

    def PopDescription(self):
        if len(self.desc_queue)>0:
            self.desc_queue.pop()
        else:
            pass

    def PushDescriptionOverride(self, in_desc):
        self.desc_override.append(in_desc)

    def PopDescriptionOverride(self):
        if len(self.desc_queue)>0:
            self.desc_override.pop()
        else:
            pass

    # Internal methods

    def __reset(self):
        self.last_error = None
        self.getvalue_queue = []
        self.desc_queue = []
        self.desc_override = []
        self.section = None
        self.section_name = ""
        self.property_name = ""

class ConfigSectionException(Exception):
    def __init__(self, code, message=None):
        if message is None:
            message = f"ConfigSection Exception {code}"
        self.code = code
        self.message = message
        super().__init__(self.message)
    