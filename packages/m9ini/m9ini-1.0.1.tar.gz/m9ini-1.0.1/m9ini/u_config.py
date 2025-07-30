# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

from .u_config_utils import *
from .u_config_parameters import *
from .u_config_section import *

import re
import os.path

class uConfig:

    __re_param = re.compile(r"^(?:([\w\:\$]+)\.)?(\w+)(?:=(\w+))?$")
    __re_header = re.compile(r"^(\[|\[\[)\s*(?:(\*\w+)\s*\:)?\s*(\$?[\w-]*)\s*(?:\:\s*(\$?[\w-]*)\s*)?(?:\:\s*([\w\s\$,-]*)\s*)?(\]|\]\])\s*$")
    __re_expand = re.compile(r"^\s*\[\s*([\w\[\]\.\=\*-]+)?\s*(?:\:\s*([\w\[\]\.\=\*-]+)?)?\s*(?:\:\s*([\w\[\]\.\=\*\,-]+)?)?\s*\]\s*=>\s*\[\s*(\$?[\w-]+)?\s*(?:\:\s*(\$?[\w-]+)?)?\s*(?:\:\s*(\$?[\w-]+)?)?\s*\]\s*$")
    __re_iterate = re.compile(r"^\s*([\d\.]+)\s*-\s*([\d\.]+)\s*(\+|\:)\s*([\d\.]+)\s*$")

    __print_failures = 0 # 0=don't print; 1=print failures; 2=print in color

    def __init__(self, Filepath=None, Parameters:uConfigParameters=None):
        '''
        If **Filepath** is specified, will load configuration from a file.

        **Parameters** provides overrides based on section matching criteria.
        '''
        self.failures = []
        self.parameters = None
        self.filepath = None

        if Filepath is None:
            self.__reset()
        else:
            self.LoadFile(Filepath, Parameters)

    def __repr__(self) -> str:
        return f"uConfig({self.filepath})"

    def LoadFile (self, Filepath, Parameters:uConfigParameters=None)->bool:
        '''
        If **Filepath** is specified, will load a configuration file.

        **Parameters** provides overrides based on section matching criteria.

        Returns *True* on success.
        '''
        self.__reset()
        self.filepath = Filepath
        self.failures = []

        if Parameters is not None:
            self.parameters = Parameters

        if os.path.isfile(Filepath) is False:
            self.add_load_failure("F01", f"Config file not found: {Filepath}")
            return False

        try:
            is_section_block = False
            is_invalid_section = False
            section_header = ['*root']
            section_base = None
            section_dict = {}
            section_list = None
            lines = self.__load_lines(Filepath, [])
            if lines is False:
                self.add_load_failure("F02", f"Failed loading configuration file: {Filepath}")
            else:
                for line in lines:
                    if len(line)>0 and (line[0] == '#' or line[0] == ';'):
                        pass
                    elif len(line)>0 and line[0] == '[':
                        skip_line = False
                        m1 = self.__re_header.match(line)
                        if m1 is None:
                            m2 = self.__re_expand.match(line)
                        if is_invalid_section:
                            is_invalid_section = False
                        else:
                            if is_section_block and m1 is None and m2 is None:
                                # special case: substitution strings in a text block
                                section_list.append(line.strip())
                                skip_line = True
                            else:
                                self.append_section(section_header, section_base, section_list if is_section_block else section_dict)

                        if skip_line is False:
                            if m1 is not None:
                                if m1[2] is not None and m1[2] not in ['*default','*override']:
                                    self.add_load_failure("F04", f"Invalid section header prefix (section ignored): {line}")
                                    is_invalid_section = True
                                else:
                                    is_section_block = m1[1]=="[["
                                    section_header = [m1[2],m1[3],m1[4],m1[5]]
                                    section_base = None
                                    section_dict = {}
                                    section_list = []
                            else:
                                if m2 is not None:
                                    is_section_block = False
                                    section_header = [None, m2[1],m2[2],m2[3]]
                                    section_base = [m2[4],m2[5],m2[6]]
                                    section_dict = {}
                                    section_list = []
                                else:
                                    self.add_load_failure("F05", f"Invalid section header (section ignored): {line}")
                                    is_invalid_section = True
                    elif is_section_block:
                        section_list.append(line.strip())
                    else:
                        pos = line.find("=")
                        if pos>0:
                            name = line[:pos].strip ()
                            if len(line)>pos+1 and line[pos+1]=='>':
                                value = line[pos+2:].lstrip().rstrip()
                                if len(value):
                                    section_dict[name] = f"^LNK^{name}^LNK^{value}"
                            else:
                                value = line[pos+1:].lstrip().rstrip()
                                if name in section_dict:
                                    if len(section_dict[name])==0:
                                        section_dict[name] = value
                                    elif len(value)>0:
                                        section_dict[name] += "," + value
                                else:
                                    section_dict[name] = value

                self.append_section(section_header, section_base, section_list if is_section_block else section_dict)

                self.apply_overrides([section for section in self.sections if section.GetBaseReference() is None])

                self.apply_expansion()

                return True
        except Exception as e:
            self.add_load_failure("F99", str(e))

        self.__reset()
        return False
    
    @classmethod
    def PrintFailures(cls, Print:bool=True, PrintColor:bool=True):
        '''
        Failures will be printed to the console.
        '''
        if Print:
            cls.__print_failures = 2 if PrintColor else 1
        else:
            cls.__print_failures = 0
    
    def HasFailures(self) -> bool:
        '''
        Returns *True* when there are failure strings available in **GetFailures()**.
        '''
        return len(self.failures)>0
    
    def GetFailures(self, Reset=True) -> list:
        '''
        Returns a list of failures since the config file was loaded.

        Returns an empty list if there are no failures.

        If **Reset** is *True*, the internal failure list will clear.
        '''
        failures = self.failures
        if Reset:
            self.failures = []
        return failures
    
    def FormatString(self, Value:str, Raw:bool=False, Params:dict=None, Empty:bool=False)->str:
        '''
        Returns a string with field replacements performed.

        If **Params** is specified, dict values will override internal property values.

        If **Empty** is *True*, an unmatched token is replaced with an empty string, otherwise it is left in place.
        '''
        ret = self.__format_value(Value, in_raw=Raw, in_params=Params, in_empty=Empty)
        return ret if ret is not None else ""
    
    @staticmethod
    def ParseSpecification(Specification:str)->list:
        '''
        Returns a list if a section specification is valid.

        **Specification** is a section specification in the format *name*, *name*:*id*, or *name*:*id*:*label*.

        Resulting list is [*name*, *id*, *label*] where entries may be *None*.
        '''
        return uConfigBase.ParseSpecification(Specification)

    # internal initialization

    def __reset (self):
        self.sections = []      # list of uConfigSection
        self.defaults = []      # list of [[section,id,label], uDictionary]
        self.overrides = []     # list of [[section,id,label], uDictionary]

    def add_load_failure(self, in_code, in_failure):
        self.add_failure(in_code, os.path.basename(self.filepath), in_failure)

    def add_failure(self, in_code, in_context, in_failure):
        if in_context is None:
            in_context = ""
        else:
            in_context = f"[+CYAN]{in_context}[+][+BLUE]:[+] "

        failure_string = f"[+BLUE][[+][+VIOLET]{in_code}[+][+BLUE]][+] {in_context}[+BLUE]{in_failure}[+]"
        failure_string_stripped = ucConsoleColor.Format(failure_string, True)
        match uConfig.__print_failures:
            case 1:
                print(failure_string_stripped)
            case 2:
                print(ucConsoleColor.Format(failure_string))
        self.failures.append(failure_string_stripped)

    def pop_failure(self):
        return self.failures.pop()

    def __find_ini(self, in_filepath, in_inifile):
        # finds an included ini file
        if os.path.isfile(in_inifile):
            return in_inifile
        if os.path.isfile(in_inifile+".ini"):
            return in_inifile+".ini"
        dir_path = os.path.dirname(in_filepath)
        in_inifile = os.path.join(dir_path, in_inifile)
        if os.path.isfile(in_inifile):
            return in_inifile
        if os.path.isfile(in_inifile+".ini"):
            return in_inifile+".ini"
        return None

    def __load_lines (self, in_filepath:str, in_loaded_list:list):

        if in_filepath in in_loaded_list:
            self.add_load_failure("F06", f"Warning: Duplicate/recursive include file reference detected: {in_filepath}")
            return []
        
        in_loaded_list.append(in_filepath)
        
        lines = []
        with open(in_filepath, "r") as f:
            for line in f:
                line = line.strip('\r\n')
                
                if len(line) > 0:
                    if line[0]=='@':
                        include_filepath = self.__find_ini(in_filepath, line[1:])
                        if include_filepath is None:
                            self.add_load_failure("F03", f"Unable to locate configuration file {line}")
                            return False
                        
                        new_lines = self.__load_lines(include_filepath, in_loaded_list)
                        if new_lines is False:
                            return False
                        
                        lines.extend(new_lines)
                    elif line[0] in ['#',';']:
                        pass
                    else:
                        lines.append(line)

        return lines

    # Access sections directly

    def GetRootSection (self)->uConfigSection:
        '''
        The root section contains any values before a section header is specified in configuration.

        Equivalent to GetSection('*root').
        '''
        return self.GetSection('*root')

    def CountSections (self, Name=None, Id=None, Label=None)->int:
        '''
        Returns a count of sections matching the specified criteria.

        **Name** can be a section specification in the format *name*, *name*:*id*, or *name*:*id*:*label*
        '''
        sret = self.GetSections(Name, Id, Label)
        if sret is None:
            return 0
        return len(sret)
    
    def GetSection (self, Name=None, Id=None, Label=None, Index=0)->uConfigSection:
        '''
        Returns a single uConfigSection, or None if not found.

        **Name** can be a section specification in the format *name*, *name*:*id*, or *name*:*id*:*label*
        '''
        if isinstance(Name, str) and Name.strip()=="":
            Name = None
        if isinstance(Id, str) and Id.strip()=="":
            Id = None

        # check if Name is a section specification
        if isinstance(Name,str) and Id is None and Label is None:
            l_spec = ucStringFormat.Strip(Name.split(':'))
            if len(l_spec)>1:
                l_spec = [None if s=='' else s for s in l_spec]
                Name = l_spec[0]
                Id = l_spec[1]
                if len(l_spec)>2:
                    Label = l_spec[2]

        cnt = 0
        for sect in self.sections:
            if sect.IsMatch(Name, Id, Label):
                if cnt == Index:
                    return sect
                cnt = cnt + 1
        return None
    
    def GetSectionById (self, Id=None)->uConfigSection:
        '''
        Returns the first section with a matching **Id**.
        '''
        return self.GetSection(Id=Id)

    def GetSectionByIndex (self, Name, Index)->uConfigSection:
        '''
        Equivalent to GetSection(Name=Name, Index=Index).
        '''
        return self.GetSection(Name=Name, Index=Index)

    def GetSections (self, Name=None, Id=None, Label=None)->list[uConfigSection]:
        '''
        Returns a list of **uConfigSection** by matching specified conditions.

        Returns an empty list if there is no match.

        **Name** can be a section specification in the format *name*, *name*:*id*, or *name*:*id*:*label*
        '''
        if isinstance(Name,str) and ':' in Name:
            spec = uConfigBase.ParseSpecification(Name)
            if isinstance(spec, list):
                Name=spec[0]
                Id=spec[1]
                Label=spec[2]

        sret = []
        for sect in self.sections:
            if sect.IsMatch(Name, Id, Label):
                sret.append(sect)
        return sret

    def GetSectionsBySpec (self, Specification:str)->list:
        '''
        Returns a list of **uConfigSection** that matches based on a section specification.
         
        **Specification** is a section specification in the format *name*, *name*:*id*, or *name*:*id*:*label*.
        '''
        spec = uConfigBase.ParseSpecification(Specification)
        if spec is False:
            return False
        
        return self.GetSections(spec[0], spec[1], spec[2])
    
    # Root access methods

    def FormatString(self, Value:str, Raw:bool=False, Params:dict=None, Empty:bool=False)->str:
        '''
        Returns a string with field replacements performed at the root level.

        If **Params** is specified, dict values will override internal property values.

        If **Empty** is *True*, an unmatched token is replaced with an empty string, otherwise it is left in place.
        '''
        return self.GetRootSection().FormatString(Value, Raw, Params, Empty)

    def NewMergedSection(self, Header:str, First:uConfigSection|dict, Second:uConfigSection|dict, Third:uConfigSection|dict=None, Raw:bool=False, Resolve:bool=True)->uConfigSection:
        '''
        Creates a new **uConfigSection** from the **First** section, merging properties in from a **Second** section.  **Second** can be a dict.

        Properties from the **First** section that are also in the **Second** section are not replaced.

        A **Third** section can be added, following the same rules.  This is optional.
        
        If **Raw** is True, only native properties are copied, not override properties.

        If **Resolve** is True, properties are resolved before before merging the values (does not apply to *dict*).

        New section is added to configuration, and so will be searchable and referencable. Overrides, defaults, and parameters will be applied.
        '''
        if not (isinstance(First, uConfigSection) and First.IsTextBlock() is False):
            return False

        if not ((isinstance(Second, uConfigSection) and Second.IsTextBlock() is False) or isinstance(Second, dict)):
            return False

        spec = uConfigBase.ParseSpecification(Header)
        if spec is False:
            return False
        
        prop1 = First if isinstance(First, dict) else First.GetProperties(Raw=Raw, Resolve=Resolve)
        prop2 = Second if isinstance(Second, dict) else Second.GetProperties(Raw=Raw, Resolve=Resolve)
        dprop = ucDictionary(self.__clear_stars(prop1))
        dprop.MergeValues(self.__clear_stars(prop2))
        if Third is not None:
            prop3 = Third if isinstance(Third, dict) else Third.GetProperties(Raw=Raw, Resolve=Resolve)
            dprop.MergeValues(self.__clear_stars(prop3))
        dprop = dprop.GetDictionary(False)
        section = uConfigSection(self, spec, dprop)
        self.apply_overrides([section])
        self.sections.append(section)

        return section
    
    def __clear_stars(self, in_dict:dict):
        d = {}
        for key in list(in_dict.keys()):
            if key.startswith('*') is False:
                d[key]=in_dict[key]
        return d

    def GetLink(self, Name)->uConfigSection:
        '''
        Returns a root section link.  Equivalent to GetSectionLink('*root', Name).

        A section link property is generally in the format {name}=>{specification}, but supports a number of syntaxes for flexibility.  See documentation for details.

        Returns *None* if there is no matching section, the property does not exist, the property is not a section link, or the section link could not resolve to a config section.
        '''
        # returns a string value
        return self.GetSectionLink('*root', Name)
       
    def HasValue(self, Name)->str:
        '''
        Returns *True* if the specified value was defined in configuration.
        
        Equivalent to HasSectionValue('*root', Name).
        '''
        # returns a string value
        return self.HasSectionValue('*root', Name)
    
    def GetValue(self, Name, Default=None)->str:
        '''
        Returns a root value.  Equivalent to GetSectionValue('*root', Name).

        If *Name* is not found, *Default* is returned.
        '''
        # returns a string value
        return self.GetSectionValue('*root', Name, Default)
    
    def GetBool(self, Name, Default=None)->bool:
        '''
        Returns a root value.  Equivalent to GetSectionBool('*root', Name).

        If *Name* is not found, *Default* is returned.
        '''
        return self.GetSectionBool('*root', Name, Default)
    
    def GetNumber(self, Name, Default=None)->int:
        '''
        Returns a root value.  Equivalent to GetSectionNumber('*root', Name).

        If *Name* is not found, *Default* is returned.
        '''
        return self.GetSectionNumber('*root', Name, Default)
    
    def GetFloat(self, Name, Default=None)->float:
        '''
        Returns a root value.  Equivalent to GetSectionFloat('*root', Name).

        If *Name* is not found, *Default* is returned.
        '''
        return self.GetSectionFloat('*root', Name, Default)
    
    def GetList(self, Name, Separator=',')->list:
        '''
        Returns a root value.  Equivalent to GetSectionList('*root', Name, Separator).
        '''
        return self.GetSectionList('*root', Name, Separator)

    # Section access methods

    def GetSectionLink(self, Section, Name, Raw=False)->uConfigSection:
        '''
        Gets a reference to a **uConfigSection** using a section specification and property name, where the property is a section link.

        **Section** can be in one of the following formats: *name*, *name*:*id*, *name*:*id*:*label*.

        A section link property is generally in the format {name}=>{specification}, but supports a number of syntaxes for flexibility.  See documentation for details.

        Returns *None* if there is no matching section, the property does not exist, the property is not a section link, or the section link could not resolve to a config section.

        If **Raw** is *True*, does not apply defaults, overrides, or parameters.
        '''
        section = self.GetSection(Section)
        if section is not None:
            return section.GetLink(Name, Raw=Raw)

        return None
    
    def HasSectionValue(self, Section, Name, Raw=False)->str:
        '''
        Returns *True* if the value was defined using a section specification by getting the first matching section.

        **Section** can be in one of the following formats: *name*, *name*:*id*, *name*:*id*:*label*.

        If the named property is a section link, a string describing the section header is returned.  If you wish to get a reference to the **uConfigSection** object, use **GetSectionLink()** instead.

        Returns *False* if there is no matching section, or the section does not have the named value.

        If **Raw** is *True*, does not apply defaults, overrides, or parameters.
        '''
        section = self.GetSection(Section)
        if section is not None:
            return section.HasValue(Name, Raw=Raw)
        return False

    def GetSectionValue(self, Section, Name, Default=None, Raw=False)->str:
        '''
        Gets a value using a section specification by getting the first matching section.

        **Section** can be in one of the following formats: *name*, *name*:*id*, *name*:*id*:*label*.

        If the named property is a section link, a string describing the section header is returned.  If you wish to get a reference to the **uConfigSection** object, use **GetSectionLink()** instead.

        Returns *Default* if there is no matching section, or the section does not have the named value.

        If **Raw** is *True*, does not apply defaults, overrides, or parameters.
        '''
        section = self.GetSection(Section)
        if section is not None:
            return section.GetValue(Name, Default=Default, Raw=Raw)
        return Default

    def GetSectionBool(self, Section, Name, Default=None)->bool:
        '''
        Gets a **bool** value using a section specification by getting the first matching section.

        **Section** can be in one of the following formats: *name*, *name*:*id*, *name*:*id*:*label*.

        Returns *Default* if there is no matching section, or the section does not have the named value.
        '''
        section = self.GetSection(Section)
        if section is not None:
            return section.GetBool(Name, Default)
        return Default
    
    def GetSectionNumber(self, Section, Name, Default=None)->int:
        '''
        Gets an *int* value using a section specification by getting the first matching section.

        **Section** can be in one of the following formats: *name*, *name*:*id*, *name*:*id*:*label*.

        Returns *Default* if there is no matching section, or the section does not have the named value.
        '''
        section = self.GetSection(Section)
        if section is not None:
            return section.GetNumber(Name, Default)
        return Default

    def GetSectionFloat(self, Section, Name, Default=None)->float:
        '''
        Gets a *float* value using a section specification by getting the first matching section.

        **Section** can be in one of the following formats: *name*, *name*:*id*, *name*:*id*:*label*.

        Returns *Default* if there is no matching section, or the section does not have the named value.
        '''
        section = self.GetSection(Section)
        if section is not None:
            return section.GetFloat(Name, Default)
        return Default

    def GetSectionList(self, Section, Name, Separator=',')->list:
        '''
        Gets a *list* using a section specification by getting the first matching section.

        **Section** can be in one of the following formats: *name*, *name*:*id*, *name*:*id*:*label*.
        '''
        section = self.GetSection(Section)
        if section is not None:
            return section.GetList(Name, Separator)
        return None
    
    # Create troubleshooting output

    def WriteConfigLines(self, Filepath:str, Resolve:bool=True, Overwrite:bool=True, Failures:bool=True):
        '''
        Writes configuration lines to a file.

        If **Resolve** is *True*, property substitutions will be performed, and all defaults, overrides and parameters will be applied.

        If **Overwrite** is *True*, any existing file will be overwritten.  Otherwise, the file will be appended to.

        If **Failures** is *True*, an error text block will be written to the end so you can see where there are substitution errors.  This is itnored when **Resolve** is *False*.

        Will replace **uStringFormat** placeholders in the **Filepath**, such as {YMD} and {TSM}.

        Returns *False* on failure, otherwise returns a path to the file that was written.
        '''

        Filepath = ucStringFormat.String(Filepath)
        if os.path.exists(Filepath) and Overwrite is False:
            return False
        
        try:
            if Resolve is False:
                Failures = False
            elif Failures:
                self.GetFailures()  # reset failures

            lines = self.BuildConfigLines(Resolve=Resolve)
            with open(Filepath, 'wt' if Overwrite else 'at') as f:
                f.writelines([line+'\n' for line in lines])

                if Failures:
                    failures = self.GetFailures(False)
                    f.write("[[WriteConfigLines_Failures]]\n")
                    f.writelines([line+'\n' for line in failures])

            return Filepath
        except Exception as e:
            pass

        return False

    def BuildConfigLines(self, Resolve:bool=True)->list:
        '''
        Returns a list of configuration lines helpful in trouble-shooting.

        If **Resolve** is *True*, property substitutions will be performed, and all defaults, overrides and parameters will be applied.

        If **Resolve** is *False*, substitutions will not be made and defauls, overrides, and parameters will be written to their own sections.
        '''
        lines = []

        if Resolve is False:
            lines.extend(self.build_parameter_lines(self.parameters))
            lines.extend(self.build_override_lines("*default", self.defaults))
            lines.extend(self.build_override_lines("*override", self.overrides))

        first=True
        for section in self.sections:
            slines = section.BuildConfigLines(Raw=(not Resolve), Resolve=Resolve)
            if first:
                first = False
                if slines[0]=="[*root]":
                    slines = slines[1:]
            lines.extend(slines)
            if len(slines)>0:
                lines.append('')

        return lines
    
    # Internal methods

    def build_override_lines(self, in_text, in_overrides):
        lines = []
        for o in in_overrides:
            lines.append(f"[{in_text}:{uSectionHeader.FormatSpecification(o[0])}]")
            for key in list(o[1].keys()):
                lines.append(f"{key}={o[1][key]}")
            lines.append('')
        return lines

    def build_parameter_lines(self, in_parameters):
        lines = []
        if isinstance(in_parameters, list):
            reorg = {}
            for param in in_parameters:
                m = self.__re_param.match(param)
                if m is not None:
                    if m[1] not in reorg:
                        reorg[m[1]] = {}
                    reorg[m[1]][m[2]] = m[3] if m[3]!='' else 'True'

            keys = list(reorg.keys())
            if len(keys)>0:
                lines.append("### PARAMETERS #########")
                for key in keys:
                    lines.extend(self.build_override_lines("*override", [([key], reorg[key])]))
                lines.pop()
                lines.append("########################")
                lines.append('')

        return lines

    def safe_list(self, in_list, in_index):
        if in_index < len(in_list):
            if isinstance(in_list[in_index], str):
                if in_list[in_index].strip()=='':
                    return None
                return in_list[in_index].strip()
        return None

    def append_section (self, in_header, in_base, in_data):
        m_first = uConfigBase.none_str(self.safe_list(in_header, 0))
        m_name = m_first if m_first=='*root' else uConfigBase.none_str(self.safe_list(in_header, 1))
        m_id = uConfigBase.none_str(self.safe_list(in_header, 2))
        m_label = uConfigBase.none_str(self.safe_list(in_header, 3))
        if isinstance(in_data, dict):
            if in_base is None:
                if m_first=='*default' or m_first=='*override':
                    # override rule
                    m_list = [m_name, m_id, m_label]
                    if m_first=='*default':
                        self.defaults.append([m_list, in_data])
                    if m_first=='*override':
                        self.overrides.append([m_list, in_data])
                else:
                    # traditional section
                    self.sections.append(uConfigSection(self, [m_name,m_id,m_label], in_data))
            else:
                # section expansion
                self.sections.append(uConfigSection(self, [m_name,m_id,m_label], in_data, in_base))
        elif isinstance(in_data, list):
            # text block section
            self.sections.append(uConfigSection(self, [m_name,m_id,m_label], in_data))

    def apply_expansion (self):
        # apply section expansion logic
        order = 0
        for section in self.sections:
            order += 1
            section.expansion_order = order

        expand_sections = [section for section in self.sections if section.GetBaseReference()]
        if len(expand_sections)==0:
            return
        
        self.sections = [section for section in self.sections if section.GetBaseReference() is None]
        org_sections_len = len(self.sections)

        new_sections = []

        passes = 9
        while len(expand_sections)>0 and passes>0:
            passes -= 1

            retry_sections = []
            for section in expand_sections:
                base_reference = section.GetBaseReference()
                if base_reference==[None,None,None]:
                    base_sections = [None]
                else:
                    base_sections = self.GetSections(base_reference[0], base_reference[1], base_reference[2])
                if len(base_sections)==0:
                    retry_sections.append(section)
                else:
                    for base_section in base_sections:
                        # get vector properties (if any)
                        vectors = []
                        prop = section.GetProperties(Raw=True, Resolve=False)
                        for key in list(prop.keys()):
                            if key.startswith('*') is False:
                                if prop[key].startswith("|") and prop[key][-1:]=="|":
                                    specification = prop[key][1:-1]
                                    section_block = self.GetSection(specification)
                                    if section_block is not None:
                                        if section_block.IsTextBlock():
                                            lines = section_block.GetTextBlock()
                                            if len(lines)>0:
                                                vectors.append({'name':key, 'values':lines})
                                        else:
                                            prop2 = section_block.GetProperties(Resolve=False)
                                            lines = [prop2[pkey] for pkey in list(prop2.keys()) if pkey.startswith('*') is False]
                                            if len(lines)>0:
                                                vectors.append({'name':key, 'values':lines})
                                    else:
                                        match = uConfig.__re_iterate.findall(specification)
                                        if len(match)==1 and len(match[0])==4:
                                            try:
                                                m = match[0]
                                                start = float(m[0])
                                                end = float(m[1])
                                                step = float(m[3])
                                                if start>=end:
                                                    self.add_load_failure("F12", f"Section expansion field is invalid, begin must be less than end: {prop[key]}")
                                                else:
                                                    values = []
                                                    if m[2]==':':
                                                        step = (end-start)/(max(step, 2)-1)
                                                    while start<=end:
                                                        values.append(start)
                                                        start += step
                                                        start = float(f"{start:0.3f}")
                                                    vectors.append({'name':key, 'values':values})
                                                pass
                                            except:
                                                self.add_load_failure("F13", f"Section expansion field is invalid numerical iteration: {prop[key]}")
                                        else:
                                            evaluate = f"[{prop[key][1:-1]}]"
                                            ev_str = section.FormatString(evaluate)
                                            if evaluate==ev_str:
                                                self.add_load_failure("F11", f"Section expansion field using |reference| must be a section, text block, numerical iteration, or evaluate to a string property: {prop[key]}")
                                            else:
                                                ev_str = ev_str.strip()
                                                if ev_str!='':
                                                    lines = [line.strip() for line in ev_str.split(',')]
                                                    vectors.append({'name':key, 'values':lines})
                                else:
                                    slist = prop[key].split('|')
                                    if len(slist)>1:
                                        slist = [s.strip() for s in slist]
                                        vectors.append({'name':key, 'values':slist})

                        if len(vectors)==0:
                            vectors = [{'name':None, 'values':[None]}]

                        section.base = base_section
                        vectors = self.__expand_vectors(None, vectors)
                        for vector in vectors:
                            uConfigSection._section_lock.PushDescriptionOverride(f"[{section.GetSpecification()}]")
                            vector['base'] = base_section
                            name = section.FormatString(section.GetName(), Params=vector)
                            id = section.FormatString(section.GetId(), Params=vector)
                            labels = section.FormatString(section.GetLabels(), Params=vector)
                            uConfigSection._section_lock.PopDescriptionOverride()

                            d = section.GetDictionary()
                            for vkey in list(vector.keys()):
                                if vkey not in [None,'base']:
                                    d[vkey] = str(vector[vkey])
                            new_section = uConfigSection(self, [name,id,labels], d, base_section)
                            new_section.expansion_order = section.expansion_order
                            new_sections.append(new_section)

            expand_sections = retry_sections

            self.sections.extend(new_sections)
            self.apply_overrides(new_sections)
            new_sections = []

        # ensure consistent expansion order
        if len(self.sections) > org_sections_len:
            self.sections = sorted(self.sections, key=lambda x: x.expansion_order)
        for section in self.sections:
            del section.expansion_order

        for section in expand_sections:
            baseref = section.GetBaseReference()
            self.add_load_failure("F10", f"Base section not found for section expansion [{section.GetSpecification()}] => [{uSectionHeader.FormatSpecification(baseref)}]")

    def __expand_vectors (self, in_build:list, in_vectors:list):
        if len(in_vectors)==0:
            return in_build

        build = []
        name = in_vectors[0]['name']
        if in_build is None:
            for value in in_vectors[0]['values']:
                build.append({name:value})
        else:
            for inbuild in in_build:
                for value in in_vectors[0]['values']:
                    d = inbuild.copy()
                    d[name]=value
                    build.append(d)

        return self.__expand_vectors(build, in_vectors[1:])

    def apply_overrides (self, in_sections):
        # applies default and override configurations and applies to matching sections
        # last matching configuration will be used
        sections = in_sections if in_sections is not None else self.sections

        for section in sections:
            section.reset_overrides()

        for sd in self.defaults:
            for section in sections:
                if section.IsMatch(sd[0][0], sd[0][1], sd[0][2]):
                    section.add_defaults(sd[1])

        for so in self.overrides:
            for section in sections:
                if section.IsMatch(so[0][0], so[0][1], so[0][2]):
                    section.add_overrides(so[1])

        if self.parameters is not None:        
            for section in sections:
                section.set_parameters(self.parameters)

        for section in sections:
            section.reset_cache()
