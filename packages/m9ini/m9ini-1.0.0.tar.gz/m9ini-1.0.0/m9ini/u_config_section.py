# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

from .u_config_utils import *
from .u_config_parameters import *
from .u_config_base import *
from .u_config_lock import *

import random

class uSectionHeader:

    def __init__(self, Name, Class=None, Id=None, Labels=None):
        self.section_id = ucStringFormat.Strip (Id)
        self.section_name = ucStringFormat.Strip (Name)
        self.section_class = ucStringFormat.Strip (Class)
        if isinstance(Labels, str):
            Labels = Labels.split(',')
        self.section_labels = ucStringFormat.Strip (Labels)
                 
    def GetId(self)->str:
        return self.section_id

    def GetName(self)->str:
        return self.section_name

    def GetClass(self)->str:
        return self.section_name if self.section_class is None else self.section_class
    
    @staticmethod
    def FormatSpecification(InList:list):
        if isinstance(InList, list):
            while len(InList)<3:
                InList.append(None)
            InList = [x if x is not None else "" for x in InList]
            spec=InList[0]
            if InList[1]!='' or InList[2]!='':
                spec+=":"+InList[1]
            if InList[2]!='':
                spec+=":"+InList[2]
            return spec
        return None
    
    def GetSpecification(self, IncludeLabels=False):
        labels = None
        if IncludeLabels and self.section_labels is not None and len(self.section_labels)>0:
            labels = ','.join(self.section_labels)
        return uSectionHeader.FormatSpecification([self.section_name, self.section_id, labels])
    
    def HasValue(self, Name)->bool:
        match Name:
            case '*id': return (self.section_id is not None)
            case '*name': return (self.section_name is not None)
            case '*class': return (self.section_class is not None)
        return False

    def GetValue(self, Name)->str:
        match Name:
            case '*id': return self.GetId()
            case '*name': return self.GetName()
            case '*class': return self.GetClass()
        return None

    def HasLabel (self, Label)->bool:
        if self.section_labels is None:
            return False
        
        if Label.startswith('$'):
            for label in self.section_labels:
                if self.__strmatch(Label, label):
                    return True
            return False

        return (Label in self.section_labels)
    
    def GetLabels (self)->str:
        if self.section_labels is None:
            return None
        return ','.join(self.section_labels)

    def IsMatch (self, Name=None, Id=None, Label=None)->bool:
        '''
        Returns True when the section matches all of the specified criteria.

        Critiera starting with $ means "starts with".
        '''
        if Name is not None and Name != '' and self.__strmatch(Name, self.GetName()) == False:
            return False

        if Id is not None and Id != '' and self.__strmatch(Id, self.GetId()) == False:
            return False

        if Label is not None and Label != '' and self.HasLabel(Label) is False:
            return False

        return True
    
    def __strmatch (self, in_match, in_str):
        if in_str is None:
            return False

        # supports start with
        if in_match[:1] == '$':
            return in_str.startswith(in_match[1:])

        return (in_match == in_str)

class uConfigSection (ucDictionary):

    # [={replace}] where replace may contain \w.?:
    __re_suball = re.compile(r'(\[=(>?)([\w\.\?\*\$-:]+)\])')
    # {name}[.{sub1|?}[.{?}]]
    __re_subthis = re.compile(r'^([\w\*]+)(?:\.((?:[\w\*]+)|\?))?(?:\.((?:[\w\*]+)|\?))?(?:\.((?:[\w\*]+)|\?))?(?:\.((?:[\w\*]+)|\?))?(?:\.((?:[\w\*]+)|\?))?(?:\.((?:[\w\*]+)|\?))?(?:\.((?:[\w\*]+)|\?))?(?:\.((?:[\w\*]+)|\?))?(?:\.((?:[\w\*]+)|\?))?$')
    # [{section}]:{id}[.{name|?}][.{?}]]
    __re_subthat = re.compile(r'^((?:\$?[\w-]+)?)(?:\:(\$?[\w-]+))?\.((?:[\*\$]?\w+)|\?)(?:\.((?:[\*\$]?\w+)|\?))?(?:\.((?:[\*\$]?\w+)|\?))?(?:\.((?:[\*\$]?\w+)|\?))?(?:\.((?:[\*\$]?\w+)|\?))?(?:\.((?:[\*\$]?\w+)|\?))?(?:\.((?:[\*\$]?\w+)|\?))?(?:\.((?:[\*\$]?\w+)|\?))?(?:\.((?:[\*\$]?\w+)|\?))?$')
    # [#] - is the value a number?
    __re_subnumber = re.compile(r'^(\d+)$')

    _section_lock = ConfigSectionLock()
    __supress_failure_messages = 0

    def __repr__(self) -> str:
        spec = self.section_header.GetSpecification(True)
        return f"[{spec if spec!='' else '*'}]"

    def __init__(self, Config, Header:list, Data:dict|list, Base:list=None):
        '''
        Provide a Header and dict to initialize.

        **Header** may be a list: [*name*, *id*, *label*].  *label* may be comma delimited.
        **Header** may be a string: *name*:*id*:*label*.  *label* may be comma delimited.
        '''
        super().__init__(Data)
        self.config = Config
        self.overrides = {}
        self.cache = None
        self.base = Base
        self.section_header = None

        # for backwards source references
        self.source_reference = []

        section_id = None
        section_name = None
        section_class = None
        section_labels = []

        # section is a text block
        self.text_block = None
        if isinstance(Data, list):
            self.text_block = Data
            while len(self.text_block)>0 and self.text_block[-1].strip()=="":
                del self.text_block[-1]

        # name and id are from header
        if isinstance(Header,str):
            Header = uConfigBase.ParseSpecification(Header)
        section_name = uConfigBase.none_str(Header[0])
        section_id = uConfigBase.none_str(Header[1])
        section_labels = uConfigBase.none_str(Header[2])
        if section_labels is not None:
            section_labels = section_labels.split(',')

        if self.HasValue("*id", Raw=True):
            section_id = uConfigBase.none_str (self.GetValue("*id", Raw=True))

        if self.HasValue("*class", Raw=True):
            section_class = uConfigBase.none_str (self.GetValue("*class", Raw=True))

        if self.HasValue("*label", Raw=True):
            section_labels = self.GetValue("*label", Raw=True).split(',')

        self.section_header = uSectionHeader(section_name, section_class, section_id, section_labels)

    # section identification

    def GetConfig (self):
        return self.config

    def GetHeader (self)->uSectionHeader:
        return self.section_header

    def GetId (self)->str:
        return self.section_header.GetId()

    def GetName (self)->str:
        return self.section_header.GetName()

    def GetClass (self)->str:
        return self.section_header.GetClass()
    
    def GetLabels (self)->str:
        return self.section_header.GetLabels()
    
    def GetSpecification(self)->str:
        '''
        Combines name and id together into a section specification.
        '''
        return self.section_header.GetSpecification() if self.section_header else ""

    def HasLabel (self, in_label)->bool:
        return self.section_header.HasLabel(in_label)

    def IsMatch (self, Name=None, Id=None, Label=None)->bool:
        '''
        Returns True when the section matches all of the specified criteria.

        Criteria starting with $ means "starts with"
        '''
        return self.section_header.IsMatch(Name, Id, Label)
    
    # Section expansion features

    def GetBaseReference (self)->list:
        '''
        Used internally for section expansion.
        '''
        return self.base

    # Text block access

    def IsTextBlock(self):
        return isinstance(self.text_block, list)
    
    def GetTextBlock(self):
        return self.text_block

    # Property access

    def GetPropertyNames(self, Raw=False, ExcludeStar=True)->list:
        '''
        Returns a *list* of all property names in this section.

        If **Raw** is *True*, does not apply parameters, overrides, or defaults.

        Special "star" properties will be excluded unless **ExcludeStar** is *False*.
        '''
        propdict = self.GetProperties(Raw)
        return [pkey for pkey in list(propdict.keys()) if pkey.startswith("*") is False or ExcludeStar is False]

    def GetProperties(self, Raw=False, Resolve=True, in_debug=False)->dict:
        '''
        Returns a *dict* containing all section properties after applying parameters, overrides, and defaults.

        If **Raw** is *True*, does not apply parameters, overrides, or defaults.

        If **Resolve** is *True*, substitutions and other references will be resolved, if possible.

        Includes special "star" properties.
        '''
        prop = ucDictionary({'*id':self.GetId(), '*class':self.GetClass(), '*name':self.GetName()})
        if Raw is False:
            for okey in list(self.overrides.keys()):
                prop.SetValue(self.overrides[okey]['name'], self.overrides[okey]['value'])

        prop.MergeValues(self.dict)

        if Raw is False:
            if isinstance(self.base, uConfigSection):
                prop2 = self.base.GetProperties(Raw=Raw, Resolve=False, in_debug=True) # will resolve below
                prop.MergeValues(prop2)
        
        dprops = prop.GetDictionary(False)
        if Resolve is True:
            for p in list(dprops.keys()):
                if p.startswith('*') is False:
                    v = None
                    if isinstance(dprops[p], uConfigSection):
                        v = self.GetLink(p)
                    elif isinstance(dprops[p], str):
                        if dprops[p].startswith("^LNK^"):
                            v = self.GetLink(p, Raw=Raw)
                        else:
                            v = self.GetValue(p, Raw=Raw)
                    # if v is not None:
                    dprops[p] = v
        else:
            for p in list(dprops.keys()):
                if p.startswith('*') is False:
                    if isinstance(dprops[p], uConfigSection):
                        dprops[p] = f"[{dprops[p].GetSpecification()}]"
                    elif isinstance(dprops[p], str):
                        if in_debug is False:
                            dprops[p] = uConfigBase.FormatLink(dprops[p])

        return dprops
    
    # Troubleshooting
    
    def BuildConfigLines(self, Raw=False, Resolve=True)->list:
        '''
        Returns a *list* of lines that is a close equivalence to lines found in a config file.

        If **Raw** is *True*, parameters, overrides, and defaults will be included.

        If **Resolve** is *True*, substitutions and other references will be resolved, if possible.
        '''
        lines = []

        if self.IsTextBlock():
            # header
            spec = self.section_header.GetSpecification(True)
            lines.append(f"[[{spec}]]")

            lines.extend(self.GetTextBlock())
        else:
            prop = self.GetProperties(Raw=Raw, Resolve=Resolve)

            # header
            spec = self.section_header.GetSpecification(True)
            lines.append(f"[{spec}]")

            # class override
            cls = self.GetClass()
            if cls is not None and cls!=self.GetName():
                lines.append(f"*class={cls}")

            # expanded base
            if isinstance(self.base,uConfigSection):
                lines.append(f"base=[{self.base.GetSpecification()}]")

            # properties
            for p in list(prop.keys()):
                if p.startswith("*") is False:
                    if isinstance(prop[p], uConfigSection):
                        lines.append(f"{p}=>[{prop[p].GetSpecification()}]")
                    else:
                        lines.append(f"{p}={prop[p]}")

        return lines
    
    # Dictionary access

    def HasValue(self, Name, Raw=False)->bool:
        '''
        Returns *True* if a named configuration value is available.

        If **Raw** is *True*, skips parameters, overrides, etc.
        '''

        if Raw is True:
            return super().HasValue(Name)

        if Name.startswith('*'):
            return self.section_header.HasValue(Name)

        if super().HasValue(Name):
            return True

        if Name in self.overrides:
            return True
        
        if isinstance(self.base, uConfigSection):
            return self.base.HasValue(Name)

        return False
    
    def __add_failure(self, in_code, in_failure):
        if self.config and uConfigSection.__supress_failure_messages==0:
            uConfigSection._section_lock.SetLastError(in_code)
            context = f"{uConfigSection._section_lock.GetSectionName()}.{uConfigSection._section_lock.GetPropertyName()}"
            if uConfigSection._section_lock.TestSection(self) is False:
                # context += f"=>[{self.GetSpecification()}]"
                pass
            self.config.add_failure(in_code, f"{context}", in_failure)

    def __get_property_list(self, in_raw=False)->set:
        # returns a set of property names on this section
        properties = set([x for x in list(self.dict.keys()) if x.startswith('*') is False])
        if in_raw is False:
            properties.update(list(self.overrides.keys()))
        return properties
    
    def GetLink(self, Name, Raw=False):
        '''
        Gets a reference to a **uConfigSection** from a property where the property is a section link.

        A section link property is generally in the format {name}=>{specification}, but supports a number of syntaxes for flexibility.  See documentation for details.

        Returns *None* if the property does not exist, the property is not a section link, or the section link could not resolve to a config section.

        If **Raw*** is *True*, does not apply defaults, overrides, or parameters.
        '''
        if Name=="base" and self.base is not None:
            return self.base
        
        value = self.__realvalue(Name, in_raw=Raw)
        if isinstance(value, uConfigSection):
            return value
        link = self.__getlinksection(f"{self.GetSpecification()}.{Name}", value, in_raw=Raw)
        return link if isinstance(link, uConfigSection) else None
    
    def GetValue(self, Name, Default=None, Raw=False)->str:
        '''
        Returns a configuration value, using the following priority:
        1. If *Name* is one of "*id", "*class", "*name", calls GetId(), GetClass(), or GetName()
        2. Returns a named parameter
        3. Returns a configured override (from configuration)
        4. Retrieves value from configuration
        5. Returns a configured default (from configuration)
        6. Returns **Default**

        If **Raw** is *True*, skips parameters, overrides, etc:
        1. Retrieves value from configuration
        2. Returns **Default**

        If the named property is a section link, returns a string representation of the section.  If you would like a **uConfigSection**, use **GetLink()** instead.
        '''
        # disable cache for backwards references
        cache = None
        if len(self.source_reference)==0 and self.cache is not None:
            cache = self.cache[str(Raw)]
            if cache is not None and Name in cache and cache[Name] is not None:
                return cache[Name]
            
        try:
            value = self.__getvalue(Name, Raw)
        except ConfigSectionException as e:
            value = None

        if cache is not None and Name in cache:
            cache[Name] = value

        return Default if value is None else value

    def __getvalue(self, Name, Raw=False)->str:
        # recursion limit check
        if uConfigSection._section_lock.Lock(self, Name) is False:
            self.__add_failure("E20", f"Exceeded maximum reference depth")
            return None
        
        getvalue_hash = f"{id(self)}:{Name}:{Raw}"

        # sub-recursion check
        if uConfigSection._section_lock.RecursionError():
            return uConfigSection._section_lock.Unlock(None, getvalue_hash)

        # self-reference check
        if uConfigSection._section_lock.PushGetValue(getvalue_hash) is False:
            self.__add_failure("E19", f"Detected recursive self-reference in [{self.GetSpecification()}].{Name}")
            uConfigSection._section_lock.Unlock(None)
            raise ConfigSectionException("E19")

        try:
            if Name=="base" and isinstance(self.base, uConfigSection):
                return uConfigSection._section_lock.Unlock(f"[{self.base.GetSpecification()}]", getvalue_hash)
            
            if Raw is not True:
                if Name=='?':
                    # random element
                    pset = self.__get_property_list()
                    if len(pset)==0:
                        return uConfigSection._section_lock.Unlock(None, getvalue_hash)
                    return uConfigSection._section_lock.Unlock(self.GetValue(random.choice(list(pset))), getvalue_hash)
                
                match Name:
                    case "*id":
                        return uConfigSection._section_lock.Unlock(self.GetId(), getvalue_hash)
                    case "*class":
                        return uConfigSection._section_lock.Unlock(self.GetClass(), getvalue_hash)
                    case "*name":
                        return uConfigSection._section_lock.Unlock(self.GetName(), getvalue_hash)
                    
                if Name in self.overrides:
                    return uConfigSection._section_lock.Unlock(self.__format_value(f"{Name}={self.overrides[Name]['value']}", self.overrides[Name]['value']), getvalue_hash)

            value = super().GetValue(Name)
            if value is None and Raw is False and isinstance(self.base, uConfigSection):
                value = self.base.__getvalue(Name, Raw=False)
            if value is not None:
                if uConfigSection._section_lock.RecursionError():
                    return uConfigSection._section_lock.Unlock(value, getvalue_hash)
                
                return uConfigSection._section_lock.Unlock(self.__format_value(f"{Name}={uConfigBase.FormatLink(value)}", value, Raw), getvalue_hash)
            
        except ConfigSectionException as e:
            return uConfigSection._section_lock.Unlock(None, getvalue_hash)

        except Exception as e:
            self.__add_failure("E99", str(e))

        return uConfigSection._section_lock.Unlock(None, getvalue_hash)
    
    def FormatString(self, Value:str, Raw:bool=False, Params:dict=None, Empty:bool=False)->str:
        '''
        Returns a string with field replacements performed.

        If **Params** is specified, dict values will override internal property values.

        If **Empty** is *True*, an unmatched token is replaced with an empty string, otherwise it is left in place.
        '''
        ret = self.__format_value(f"FormatString(\"{Value}\")", Value, in_raw=Raw, in_params=Params, in_empty=Empty)
        return ret if ret is not None else ""

    # Helper methods

    def GetBool(self, Name, Default=None)->bool:
        return ucType.ConvertToBool(self.GetValue(Name, Default))

    def GetNumber(self, Name, Default=None)->int:
        return ucType.ConvertToInt(self.GetValue(Name, Default))

    def GetFloat(self, Name, Default=None)->float:
        return ucType.ConvertToFloat(self.GetValue(Name, Default))

    def GetList(self, Name, Separator=',')->list:
        return ucType.ConvertToList(self.GetValue(Name))
    
    # modify native properties

    def ClearProperty(self, Name):
        '''
        Clears a property.
        
        Only native properties are effected.  Defaults, overrides, and parameters are still applied.
        '''
        if Name.startswith('*') is False and super().HasValue(Name):
            super().ClearValue()
            self.config.apply_overrides([self])
            return True

        return False

    def SetProperty(self, Name, Value):
        '''
        Sets a property.  **Value** will be converted to a string value.
        
        Only native properties are effected.  Defaults, overrides, and parameters are still applied.

        If **Value** is None, the property will be cleared.
        '''
        if Value is None:
            return self.ClearProperty(Name)
        elif Name.startswith('*') is False:
            super().SetValue(Name, str(Value))
            self.config.apply_overrides([self])
            return True

        return False

    def SetLink(self, Name, Section):
        '''
        Adds a property that is a link to another section.

        **Section** is a **uConfigSection**.

        The property **Name** can then be used in substitution syntax.
        '''
        if isinstance(Section, uConfigSection) and Name.startswith('*') is False:
            super().SetValue(Name, Section)
            self.config.apply_overrides([self])
            return True

        return False

    # private methods for use by uConfig

    def reset_overrides(self):
        self.overrides = {}

    def __add_override(self, in_name, in_value, in_type, in_level=0):
        # overrides have a priority, and if an override already exists of higher priority, then no change will be made
        # in_type: 0=default; 1=override; 2=parameter; higher levels take priority
        # in_level: lower levels take priority
        if in_type==0 and super().HasValue(in_name):
            return  # value exists, so ignore default
        if in_name in self.overrides:
            if self.overrides[in_name]['type'] > in_type:
                return # existing override takes priority based on type
            elif self.overrides[in_name]['type']==in_type:
                # same type, based on level; note if they are the same level, do not replace
                if self.overrides[in_name]['level'] <= in_level:
                    return # same type, but lower level (or first use) takes priority
        self.overrides[in_name] = {'name':in_name, 'value':in_value, 'type':in_type, 'level':in_level}     

    def add_defaults (self, in_values):
        # in_values can be a dict or uDictionary
        if isinstance(in_values, dict):
            in_values = ucDictionary(in_values)
        if isinstance(in_values, ucDictionary):
            level = in_values.GetNumber("*level", 0)
            for key in in_values.GetKeys():
                if key.startswith("*") is False:
                    self.__add_override(key, in_values.GetValue(key), 0, level)

    def add_overrides (self, in_values):
        # in_values can be a dict or uDictionary
        if isinstance(in_values, dict):
            in_values = ucDictionary(in_values)
        if isinstance(in_values, ucDictionary):
            level = in_values.GetNumber("*level", 0)
            for key in in_values.GetKeys():
                if key.startswith("*") is False:
                    self.__add_override(key, in_values.GetValue(key), 1, level)

    def set_parameters (self, in_parameters:uConfigParameters):
        # in_parameters should be a uConfigParameters or list of string parameters
        if isinstance(in_parameters, list):
            in_parameters = uConfigParameters(in_parameters)
        if isinstance(in_parameters, uConfigParameters):
            params = in_parameters.GetAllParameters()
            for param in params:
                if self.IsMatch(param[0],param[1],param[2]):
                    self.__add_override(param[3],param[4],2)

    def reset_cache(self):
        self.cache = {str(True): {}, str(False): {}} # raw?

        prop = self.GetProperties(Raw=True, Resolve=False)
        for pkey in list(prop.keys()):
            if prop[pkey] is not None and isinstance(prop[pkey],str) and "[=" in prop[pkey]:
                self.cache[str(True)][pkey] = None

        prop = self.GetProperties(Raw=False, Resolve=False)
        for pkey in list(prop.keys()):
            if prop[pkey] is not None and isinstance(prop[pkey],str) and "[=" in prop[pkey]:
                self.cache[str(False)][pkey] = None

    def __getlinksection(self, in_replace, in_element, in_raw):
        # returns a configuration section based on a link property value
        # returns FALSE if the element is a valid link, but cannot be resolved
        # returns None if the element is not a valid link
        if isinstance(in_element,str):
            if in_element.startswith("^LNK^"):
                s = in_element.split("^LNK^")
                if len(s)==3:
                    r = s[2].split(':')
                    if len(r)==1:
                        # [6.1] `{property}=>{section}` Link to a remote section
                        r[0] = self.__format_value(in_replace, r[0], in_raw)
                        section = self.__get_section(r[0], None, in_raw)
                        if section is None:
                            self.__add_failure("E01", f"Link \"{s[1]}=>{s[2]}\" does not specify a valid section")
                        else:
                            return section
                    elif len(r)==2:
                        # [6.2] `{property}=>{section}:{id}` Link to a remote section (with id)
                        # [6.3] `{property}=>:{id}` Link to a remote section (id only)
                        r[0] = self.__format_value(in_replace, r[0], in_raw)
                        r[1] = self.__format_value(in_replace, r[1], in_raw)
                        section = self.__get_section(r[0], r[1], in_raw)
                        if section is None:
                            self.__add_failure("E01", f"Link \"{s[1]}=>{s[2]}\" does not specify a valid section")
                        else:
                            return section
                    else:
                        self.__add_failure("E02", f"Link \"{s[1]}=>{s[2]}\" is not a valid specification")

                    # a valid link that cannot be resolved
                    return False
            
        return None
    
    def __realvalue(self, in_name, in_raw):
        # helper method to get real value without resolution
        if in_name in ['*id','*name','*class']:
            return self.__getvalue(in_name)
        if in_raw is False and in_name in self.overrides:
            return self.overrides[in_name]['value']
        v =  super().GetValue(in_name)
        if v is None and in_raw is False and isinstance(self.base, uConfigSection):
            v = self.base.__realvalue(in_name, in_raw)
        return v
            
    def __subvalue(self, in_replace:str, in_element, in_tokens:list, in_raw, in_params):
        # recursive method
        # returns None on failure

        if uConfigSection._section_lock.RecursionError():  # Recursion exceptions
            return None

        if len(in_tokens)==0 or in_tokens[0]=='':
            if isinstance(in_element, uConfigSection):
                self.__add_failure("E03", f"Replacement is a link to a section without any property specified{self.__instr(in_replace)}")
                return f"[{in_element.GetSpecification()}]"
            return in_element
        
        # check for a link property
        if isinstance(in_element, uConfigSection) is False:
            section = self.__getlinksection(in_replace, in_element, in_raw)
            if section is False:
                return None # link could not be resolved
            if section is not None:
                return self.__subvalue(in_replace, section, in_tokens, in_raw, in_params)

        if in_tokens[0]=='?':
            if isinstance(in_element, uConfigSection):
                if in_element.IsTextBlock():
                    # random line of a text block
                    text = in_element.GetTextBlock()
                    if len(text)==0:
                        self.__add_failure("E06", f"Random (text block contains no lines){self.__instr(in_replace)}")
                        return None
                    else:
                        return self.__subvalue(in_replace, random.choice(text), in_tokens[1:], in_raw, in_params)
                else:
                    # random property of a config section
                    value = in_element.GetValue('?', Raw=in_raw)
                    if value is None:
                        self.__add_failure("E07", f"Random (section contains no properties){self.__instr(in_replace)}")
                        return None
                    else:
                        return self.__subvalue(in_replace, value, in_tokens[1:], in_raw, in_params)
            else:
                return self.__subvalue(in_replace, random.choice(in_element.split(',')).strip(), in_tokens[1:], in_raw, in_params)
        else:
            if isinstance(in_element, uConfigSection):
                if in_element.IsTextBlock():
                    # replace token with property value if it starts with $
                    if isinstance(in_tokens[0], str) and in_tokens[0].startswith('$'):
                        # [5.13] Property name redirect to a local property
                        new_token = self.GetValue(in_tokens[0][1:])
                        if new_token is None:
                            self.__add_failure("E13", f"Property indirection failure (\"{in_tokens[0][1:]}\" not found){self.__instr(in_replace)}")
                            return None
                        temp_list = list(in_tokens)
                        temp_list[0] = new_token
                        in_tokens = tuple(temp_list)

                    m = self.__re_subnumber.match(in_tokens[0])
                    if m is not None:
                        index=int(m[1])
                        lines=in_element.GetTextBlock()
                        if index<len(lines):
                            return self.__subvalue(in_replace, lines[index], in_tokens[1:], in_raw, in_params)
                        else:
                            self.__add_failure("E08", f"Invalid index (of a text block){self.__instr(in_replace)}")
                            return None
                    else:
                        self.__add_failure("E09", f"Invalid property (of a text block){self.__instr(in_replace)}")
                        return None
                else:
                    # return section property
                    value = None
                    if in_params is not None and in_tokens[0] in in_params and in_params[in_tokens[0]] is not None:
                        # return value from parameters
                        if isinstance(in_params[in_tokens[0]], uConfigSection):
                            return self.__subvalue(in_replace, in_params[in_tokens[0]], in_tokens[1:], in_raw, in_params=None)
                        else:
                            value = in_element.__format_value(in_replace, in_params[in_tokens[0]], in_raw=in_raw, in_params=None)
                            return self.__subvalue(in_replace, value, in_tokens[1:], in_raw, in_params=None)
                        
                    if in_tokens[0]=='base':
                        if isinstance(in_element.base, uConfigSection):
                            # base was specified, and a base exists
                            return self.__subvalue(in_replace, in_element.base, in_tokens[1:], in_raw, in_params=None)
                        else:
                            self.__add_failure("E14", f"Base section does not exist{self.__instr(in_replace)}")
                            return None
                    
                    # replace token with property value if it starts with $
                    if isinstance(in_tokens[0], str) and in_tokens[0].startswith('$'):
                        # [5.13] Property name redirect to a local property
                        new_token = self.GetValue(in_tokens[0][1:])
                        if new_token is None:
                            self.__add_failure("E13", f"Property indirection failure (\"{in_tokens[0][1:]}\" not found){self.__instr(in_replace)}")
                            return None
                        temp_list = list(in_tokens)
                        temp_list[0] = new_token
                        in_tokens = tuple(temp_list)

                    try_link = in_element.__realvalue(in_tokens[0], in_raw)
                    if isinstance(try_link, uConfigSection):
                        value = try_link
                    elif try_link is not None:
                        # see if this is a link
                        value = in_element.__getlinksection(in_replace, try_link, in_raw)
                        if value is False:
                            return None

                    if value is None:
                        # check local properties
                        value = self.__sub_expansion(in_element, in_tokens[0], in_raw=in_raw)
                    if value is None and isinstance(in_element.base, uConfigSection): 
                        # check base section properties
                        value = self.__sub_expansion(in_element.base, in_tokens[0], in_raw=in_raw)
                    if value is None and len(self.source_reference)>0:
                        # check backwards source references -- supress failures
                        uConfigSection.__supress_failure_messages += 1
                        try:
                            for si in list(reversed(range(len(self.source_reference)))):
                                value = self.source_reference[si].GetValue(in_tokens[0], Raw=in_raw)
                                if value:
                                    break
                        except:
                            pass
                        uConfigSection.__supress_failure_messages -= 1
                    if uConfigSection._section_lock.RecursionError():  # Recursion exceptions
                        return None
                    if value is None:
                        self.__add_failure("E11", f"Section property \"{in_tokens[0]}\" not found{self.__instr(in_replace)}")
                        return None
                    else:
                        return self.__subvalue(in_replace, value, in_tokens[1:], in_raw, in_params)
            else:
                if isinstance(in_element, str):
                    self.__add_failure("E12", f"Invalid property (of a string){self.__instr(in_replace)}")
                    return None

        self.__add_failure("E98", f"Unexpected scenario{self.__instr(in_replace)}")
        return None
    
    def __instr(self, in_replace):
        replace = uConfigSection._section_lock.GetDescription()
        if replace == "":
            replace = in_replace
        return f" in {replace}" if replace else ""

    def __sub_expansion(self, in_element, in_value, in_raw):
        # this is the case of an expanded value referencing source properties
        # essentially a backwards reference (a reference that couldn't be resolved by the target)
        if uConfigSection._section_lock.RecursionError():
            return None
        
        if in_element is self:
            return self.GetValue(in_value, Raw=in_raw)
        
        in_element.source_reference.extend(self.source_reference)
        in_element.source_reference.append(self)
        try:
            in_value = in_element.GetValue(in_value, Raw=in_raw)
        except Exception as e:
            in_value = None
        for i in list(range(len(self.source_reference)+1)):
            in_element.source_reference.pop()

        return in_value

    def __format_value(self, in_desc, in_value, in_raw=False, in_params=None, in_empty=False):
        if isinstance(in_value, str) is False:
            return in_value
        
        uConfigSection._section_lock.PushDescription(in_desc)
        
        if in_value.startswith("^LNK^"):
            section = self.__getlinksection(None, in_value, in_raw)
            if isinstance(section, uConfigSection):
                uConfigSection._section_lock.PopDescription()
                return f"[{section.GetSpecification()}]"
            section = None
        
        replace_all = uConfigSection.__re_suball.findall(in_value)
        for replace in replace_all:
            if replace[1]=="":
                # reference this section
                # {name}[.{sub1|?}[.{?}]]
                m = self.__re_subthis.findall(replace[2])
                if len(m)!=1:
                    self.__add_failure("E04", f"Replacement logic is not valid property syntax{self.__instr(replace[0])}")
                    if in_empty:
                        in_value = in_value.replace(replace[0], '')
                else:
                    m=m[0]
                    m_value = self.__subvalue(replace[0], self, m, in_raw, in_params)
                    if m_value is not None:
                        in_value = in_value.replace(replace[0], m_value)
                    elif in_empty:
                        in_value = in_value.replace(replace[0], '')

            elif replace[1]==">":
                # reference another section
                # [{section}]:{id}.{name|?}[.{?}]]
                m = self.__re_subthat.findall(replace[2])
                if len(m)!=1:
                    self.__add_failure("E05", f"Replacement logic is not valid pointer syntax{self.__instr(replace[0])}")
                    if in_empty:
                        in_value = in_value.replace(replace[0], '')
                else:
                    m=m[0]
                    section = self.__get_section(m[0], m[1], in_raw)
                    if section is None:
                        self.__add_failure("E10", f"Section \"{uConfigBase.BuildSpecification([m[0],m[1]])}\" not found{self.__instr(replace[0])}")
                        if in_empty:
                            in_value = in_value.replace(replace[0], '')
                    else:
                        m_value = self.__subvalue(replace[0], section, m[2:], in_raw, in_params)
                        if m_value is None:
                            # check for indirect property reference
                            value = None
                            uConfigSection.__supress_failure_messages += 1
                            try:
                                value = self.__subvalue(replace[0], self, [m[2]], in_raw, in_params)
                            except ConfigSectionException as e:
                                raise e
                            except:
                                pass
                            uConfigSection.__supress_failure_messages -= 1

                            if value is not None:
                                self.config.pop_failure()
                                vx = tuple([value]+list(m)[3:])
                                m_value = self.__subvalue(replace[0], section, vx, in_raw, in_params)
                        if m_value is not None:
                            in_value = in_value.replace(replace[0], m_value)
                        elif in_empty:
                            in_value = in_value.replace(replace[0], '')

        uConfigSection._section_lock.PopDescription()
        ret = ucStringFormat.Strip (in_value)
        return None if ret.startswith("^LNK^") else ret

    def __get_section(self, in_name, in_id, in_raw):
        # handle $ redirection
        indirection_failure = False
        if isinstance(in_name, str) and in_name.startswith('$'):
            # [5.11] Section name redirect to a local property
            new_name = self.GetValue(in_name[1:])
            if new_name is None:
                self.__add_failure("E13", f"Property indirection failure (\"{in_name[1:]}\" not found){self.__instr(None)}")
                indirection_failure = True
            in_name = new_name

        if isinstance(in_id, str) and in_id.startswith('$'):
            # [5.12] Section id redirect to a local property
            new_id = self.GetValue(in_id[1:])
            if new_id is None:
                self.__add_failure("E13", f"Property indirection failure (\"{in_id[1:]}\" not found){self.__instr(None)}")
                indirection_failure = True
            in_id = new_id

        if indirection_failure:
            return None

        section = self.config.GetSection(in_name, in_id)
        return section
