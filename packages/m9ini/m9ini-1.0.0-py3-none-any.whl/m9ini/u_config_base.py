# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

import re

class uConfigBase:

    __re_spec = re.compile(r"^\s*(\$?[\w-]*)\s*(?:\:\s*(\$?[\w-]*)\s*)?(?:\:\s*([\w\s\$,-]*)\s*)?\s*$")

    @staticmethod
    def none_str(in_str):
        if in_str is None:
            return None
        in_str = in_str.strip()
        if in_str=="":
            return None
        return in_str

    @classmethod
    def ParseSpecification(cls, Specification:str)->list:
        '''
        Returns a list if a section specification is valid.

        **Specification** is a section specification in the format *name*, *name*:*id*, or *name*:*id*:*label*.

        Resulting list is [*name*, *id*, *label*] where entries may be *None*.
        '''
        m = cls.__re_spec.match(Specification)
        if m is not None:
            return [m[1] if m[1]!='' else None, m[2] if m[2]!='' else None, m[3] if m[3]!='' else None]
        return False
    
    @classmethod
    def BuildSpecification(cls, Specification:list)->str:
        spec = ""
        if isinstance(Specification, list):
            if len(Specification)>0 and isinstance(Specification[0],str):
                spec += Specification[0]
            if len(Specification)>1 and isinstance(Specification[1],str) and Specification[1]!="":
                spec += f":{Specification[1]}"
        return spec
    
    @staticmethod
    def FormatLink(Value)->str:
        if isinstance(Value, str) and Value.startswith("^LNK^"):
            slist = Value.split("^LNK^")
            if len(slist)==3:
                return f">{slist[2]}"
        return Value

