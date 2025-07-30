# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

import re

class uConfigParameters:

    __re1 = re.compile(r"^((?P<s3>\$?\w*)\.)?(?P<name>\w+)=(?P<value>\w+)$")
    __re2 = re.compile(r"^(?P<s2>\$?\w*):((?P<s3>\$?\w*)\.)(?P<name>\w+)=(?P<value>\w+)$")
    __re3 = re.compile(r"^(?P<s1>\$?\w*):(?P<s2>\$?\w*):((?P<s3>\$?\w*)\.)(?P<name>\w+)=(?P<value>\w+)$")

    def __init__(self, Parameters:list|dict, Section=None):
        '''
        **Parameters** is a list of config overrides in the format: *section*:*id*:*label*.*name*=*value*
        - *section*:*id*:*label* is a section specification, which can be empty and any elements can be empty
        - *name*=*value* is required

        When the section specification matches a section, *name* provides an override *value*.

        The following variations are accepted:
        - *name*=*value*
        - *section*.*name*=*value*
        - *section*:*id*.*name*=*value*
        - *section*:*id*:*label*.*name*=*value*

        **Parameters** may also be a dict, in which case there is no section specification, just name-value pairs.
        - *Section* can be used to add a section specification to dict entries.
        '''

        self.config_params = []
        self.invalid_params = []
        self.named_params = []

        if isinstance(Parameters, dict):
            Parameters = uConfigParameters.ConvertDict2List(ParamsDict=Parameters, Section=Section)

        if isinstance(Parameters, list):
            for param in Parameters:
                if isinstance(param, str):
                    pparam = uConfigParameters.__parse_param(param)
                    if pparam is False:
                        self.invalid_params.append(param)
                    else:
                        self.config_params.append(pparam)
                        if pparam[3] not in self.named_params:
                            self.named_params.append(pparam[3])

    def GetInvalidParams(self)->list:
        '''
        Returns a list of malformed parameters passed into the constructor.
        '''
        if len(self.invalid_params)==0:
            return None
        
        return self.invalid_params

    def TestParam(self, in_param)->bool|list:
        '''
        Tests a parameter specification.
        Returns [section,id,label,name,value] on success.  Name and value are required.
        Returns False on failure.
        '''
        return uConfigParameters.__parse_param(in_param)
    
    def ExtractDict(self)->dict:
        '''
        Extracts parameters as a dict, eliminating any section specifications.
        '''
        params = {}
        for param in self.config_params:
            params[param[3]] = param[4]
        return params
    
    @staticmethod
    def ConvertDict2List(ParamsDict:dict, Section:str=None):
        '''
        Converts a dict to a parameters list with the given section specification.

        **Section** is an optional section specification in the format *name*:*id*:*label*, where any or all entries may be empty.
        '''

        if isinstance(Section, str):
            Section = Section.strip()
            if Section.strip()=="":
                Section = None
        else:
            Section = None

        params = []
        for key in list(ParamsDict.keys()):
            if Section is None:
                params.append(f"{key}={ParamsDict[key]}")
            else:
                params.append(f"{Section}.{key}={ParamsDict[key]}")

        return  params

    @classmethod
    def __parse_param(cls, in_param):

        m = cls.__re1.match(in_param)
        if m is not None:
            s3 = m.group('s3')
            return [s3 if s3!='' else None, None, None, m.group('name'), m.group('value')]
        else:
            m = cls.__re2.match(in_param)
            if m is not None:
                s2 = m.group('s2')
                s3 = m.group('s3')
                return [s2 if s2!='' else None, s3 if s3!='' else None, None, m.group('name'), m.group('value')]
            else:
                m = cls.__re3.match(in_param)
                if m is not None:
                    s1 = m.group('s1')
                    s2 = m.group('s2')
                    s3 = m.group('s3')
                    return [s1 if s1!='' else None, s2 if s2!='' else None, s3 if s3!='' else None, m.group('name'), m.group('value')]
                
        return False
    
    def GetAllParameters(self)->list:
        return self.config_params
    
    def GetNamedParameters(self, in_name)->list:
        '''
        Returns a list of [section,id,label,name,value] when there is a name match.

        Returns None when there are no matching parameters of the specified name.
        '''
        if in_name not in self.named_params:
            return None
        
        ret_params = []
        for param in self.config_params:
            if param[3] == in_name:
                ret_params.append(param)

        return ret_params