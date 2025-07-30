# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

import os, re, datetime

class ucType:

    @staticmethod
    def ConvertToInt(Value:str)->int:
        '''
        Converts a string **Value** to an *int*.

        Returns *False* on error
        
        Returns *None* if **Value** is None or empty.
        '''
        if Value is None or Value=="":
            return None
        try:
            return int(Value)
        except:
            pass
        return False        

    @staticmethod
    def ConvertToFloat(Value:str)->float:
        '''
        Converts a string **Value** to an *int*.

        Returns *False* on error
        
        Returns *None* if **Value** is None or empty.
        '''
        if Value is None or Value=="":
            return None
        try:
            return float(Value)
        except:
            pass
        return False        

    @staticmethod
    def ConvertToBool(Value:str)->bool:
        '''
        Converts a **Value** to a *bool*.

        Returns *True* if **Value** is *True* or "true" (case-insensitive).

        Returns *False* otherwise.
        '''
        if Value is None or Value=="":
            return None
        if isinstance(Value, bool):
            return Value
        elif isinstance(Value, str):
            return Value.lower()=="true"
        return False

    @staticmethod
    def ConvertToList(Value:str|list, Separator=","):
        '''
        Converts a string **Value** to a *list*, or returns **Value** if it is a list.

        Returns *False* on failure.
        '''
        if Value is None:
            return None
        elif isinstance(Value, list):
            return Value
        elif isinstance(Value, str):
            return ucStringFormat.Strip (Value.split (Separator))
        return False

    @staticmethod
    def SafeString(Value:str):
        '''
        Converts *Value* to a string.

        If *None*, returns an empty string.
        '''
        if Value is None:
            return ""
        return str(Value)
    
class ucStringFormat:

    re_byteunits = None
    ls_byteunits = None
    cv_byteunits = None

    re_timeunits = None
    ls_timeunits = None
    lg_timeunits = None
    cv_timeunits = None

    @classmethod
    def __init(cls):
        if cls.re_byteunits is None:
            cls.re_byteunits = re.compile(r"^(?P<bytes>\d+(.\d+)?)\s*(?P<units>(tb|gb|mb|kb|b|))$", re.IGNORECASE)
            cls.ls_byteunits = ['tb', 'gb', 'mb', 'kb', 'b']
            cls.cv_byteunits = {}
            cls.cv_byteunits['b'] = 1
            cls.cv_byteunits['kb'] = 1024
            cls.cv_byteunits['mb'] = cls.cv_byteunits['kb'] * 1024
            cls.cv_byteunits['gb'] = cls.cv_byteunits['mb'] * 1024
            cls.cv_byteunits['tb'] = cls.cv_byteunits['gb'] * 1024

            cls.re_timeunits = re.compile(r"^(?P<time>\d+(.\d+)?)\s*(?P<units>(d|h|m|s))\w*$", re.IGNORECASE)
            cls.ls_timeunits = ['d', 'h', 'm', 's']
            cls.lg_timeunits = {'d':'days', 'h':'hrs', 'm':'min', 's':'sec'}
            cls.cv_timeunits = {}
            cls.cv_timeunits['s'] = 1
            cls.cv_timeunits['m'] = cls.cv_timeunits['s'] * 60
            cls.cv_timeunits['h'] = cls.cv_timeunits['m'] * 60
            cls.cv_timeunits['d'] = cls.cv_timeunits['h'] * 24

    @classmethod
    def Bytes(cls, Bytes:int,ByteUnits:str=None)->str:
        '''
        Returns a string that describes the number of **Bytes**, converted to a unit.

        **ByteUnits** is one of: "tb", "gb", "mb", "kb", "b".

        If **ByteUnits** is *None*, units will be selected automatically.
        '''
        cls.__init()

        if ByteUnits is not None:
            ByteUnits = ByteUnits.lower()
            if ByteUnits not in cls.cv_byteunits:
                ByteUnits = None
                
        Bytes = float(Bytes)
        for u in cls.ls_byteunits:
            if ByteUnits is None:
                if Bytes/cls.cv_byteunits[u]>1:
                    ByteUnits = u
                    
        if ByteUnits is None:
            ByteUnits = 'b'
        
        if ByteUnits=="b":
            return "{:d} bytes".format(int(Bytes))
            
        return "{:.1f} ".format(Bytes/cls.cv_byteunits[ByteUnits]) + ByteUnits
    
    @classmethod
    def ParseBytes(cls, String:str)->int:
        '''
        Parses a string, converting an expression to bytes.
        
        Supports b,kb,mb,gb,tb. Case insensitive.

        For example: "12kb", "1.2 Gb", "99", "99b", "1.2345MB"

        returns False on failure
        '''
        cls.__init()

        if isinstance(String, int):
            return String
        
        try:
            m = cls.re_byteunits.match(String)
            if m is None:
                return False
            
            bytes = float(m.group("bytes"))
            units = m.group("units").lower()
            if units=='':
                units = 'b'
            bytes *= cls.cv_byteunits[units]
            return int(bytes)
        except:
            return False

    @classmethod
    def Duration(cls, Seconds:float,SecUnits:str=None)->str:
        '''
        Returns a string that describes a duration, converted to a unit of time.

        **Seconds** is specified in milliseconds.

        **SecUnits** is one of: "d", "h", "m", "s".

        If **SecUnits** is *None*, units will be selected automatically.
        '''
        cls.__init()

        if SecUnits is not None:
            SecUnits = SecUnits.lower()
            if SecUnits not in cls.ls_timeunits:
                SecUnits = None

        Seconds = float(Seconds)
        for u in cls.ls_timeunits:
            if SecUnits is None:
                if Seconds/cls.cv_timeunits[u]>1:
                    SecUnits = u
                    
        if SecUnits is None:
            SecUnits = "s"
        
        str = "{:.1f}".format(Seconds/cls.cv_timeunits[SecUnits]) + " " + cls.lg_timeunits[SecUnits]
        return str

    @classmethod
    def ParseDuration(cls, String:str)->int:
        '''
        Parses a string, converting an expression to milliseconds.
        
        Supports s,m,d,d. Case insensitive.

        For example: "12m", "1.2 Hours", "99s", "99sx", "1.2345minutes"
        '''
        cls.__init()

        try:
            m = cls.re_timeunits.match(String)
            if m is None:
                return False
            
            ms = float(m.group("time"))
            units = m.group("units").lower()
            ms *= cls.cv_timeunits[units]
            return int(ms)
        except:
            return False

    @staticmethod
    def String(String:str, Bytes:int=None, ByteUnits:str=None, Seconds:int=None, SecUnits:str=None, Now:datetime=None):
        '''
        Replaces the following tokens in a string:
        - **{YMD}**: year, month, day as YYMMDD
        - **{LTS}**: log timestamp
        - **{TSM}**: seconds since midnight as a zero-padded 5-digit number
        - **{B}**: Bytes; ByteUnits is one of ('tb', 'gb', 'mb', 'kb', 'b'); When ByteUnits is *None*, units are calculated automatically
        - **{D}**: duration from Seconds; SecUnits is one of ('d', 'h', 'm', 's'); When SecUnits is *None*, units are calculated automatically
        - **{PYF}**: environment PYFOLDER

        Now is used for **{YMD}**, **{LTS}**, and **{TSM}**.  When not specified, uses current time.
        '''
        now = Now
        if now is None:
            now = datetime.datetime.now()
        s_ymd = now.strftime("%y%m%d")
        s_lts = now.strftime("%y%m%d %H:%M:%S")
        s_tsm = "{:05d}".format((now.hour * 3600) + (now.minute * 60) + now.second)
        s_bytes = ""
        if Bytes is not None:
            s_bytes = ucStringFormat.Bytes(Bytes, ByteUnits)
        s_ms = ""
        if Seconds is not None:
            s_ms = ucStringFormat.Duration(Seconds, SecUnits)
        s_pyf = os.getenv('PYFOLDER')

        try:
            str = String.format (YMD=s_ymd, LTS=s_lts, TSM=s_tsm, B=s_bytes, D=s_ms, PYF=s_pyf)
        except:
            pass
        return str

    @staticmethod
    def Strip(Value:str|list)->str|list:
        '''
        Strips white-space from the begining and end of a string.

        If a list is provided, strips all entries of the list.
        '''
        if isinstance(Value, str):
            return Value.strip()
        if isinstance(Value, list):
            l = []
            for v in Value:
                if isinstance(v, str):
                    l.append(v.strip ())
                else:
                    l.append(v)
            return l
        return Value

class ucDictionary:
    
    def __init__(self, Dict={}):
        '''
        Initialize with a dict or uDictionary.
        '''
        if isinstance(Dict, dict):
            self.dict = Dict.copy()
        elif isinstance(Dict, ucDictionary):
            self.dict = Dict.GetDictionary()
        else:
            self.dict = {}

    def Copy(self):
        '''
        Performs a shallow copy.
        '''
        return ucDictionary(self.dict.copy())
    
    def GetKeys(self):
        return list(self.dict.keys())
        
    def GetValue(self, Name, Default=None):
        if Name in self.dict:
            return self.dict[Name]
        return Default

    def GetNumber(self, Name, Default=None):
        return ucType.ConvertToInt(self.GetValue(Name, Default))
    
    def GetFloat(self, Name, Default=None):
        return ucType.ConvertToFloat(self.GetValue(Name, Default))
    
    def GetBool(self, Name, Default=None):
        return ucType.ConvertToBool(self.GetValue(Name, Default))
    
    def GetList(self, Name, Separator=","):
        return ucType.ConvertToList(self.GetValue(Name), Separator)
    
    def SetValue(self, Name, Value):
        # set specified value
        self.dict[Name] = Value
        
    def ClearValue(self, Name):
        '''
        Remove the specified value.
        '''
        if Name in self.dict:
            del self.dict[Name]

    def HasValue(self, Name):
        return Name in self.dict
            
    def MergeValues(self, Dict, Overwrite=False):
        '''
        Takes a **dict** or **uDictionary**.

        Merges **dict** into current dictionary.

        If there is a confict on a given entry, only sets that value when **Overwrite** is *True*.
        '''
        d = None
        if isinstance(Dict, dict):
            d = Dict
        elif isinstance(Dict, ucDictionary):
            d = Dict.GetDictionary(False)
        else:
            return

        for key in d:
            if not (Overwrite==False and key in self.dict):
                self.dict [key] = d [key]
            
    def GetDictionary(self, Copy=True)->dict:
        '''
        Returns the internal **dict**, or a **Copy** of this **dict**.
        '''
        # Gets the internal python dictionary
        # Reference to internal, unless copied
        if Copy:
            return self.dict.copy()
        return self.dict

class ucConsoleColor:
    # Colors tuned to system("color")
    _codes = None
    _re_format = None

    @classmethod
    def GetCode(cls, Color):
        """
        Get a console code by color name.  Returns an empty string if **Color** is not recognized.
        """
        cls.__init_colors()
        if Color in cls._codes:
            return cls._codes[Color]
        return ""
    
    @classmethod
    def __init_colors(cls):
        if cls._codes is None:
            cls._codes = {}
            cls._codes['END'] = '\33[0m'
            cls._codes['BOLD'] = '\33[1m'
            cls._codes['ITALIC'] = '\33[3m'
            cls._codes['UNDERLINE'] = '\33[4m'
            cls._codes['RED'] = '\33[31m'
            cls._codes['GREEN'] = '\33[32m'
            cls._codes['YELLOW'] = '\33[33m'
            cls._codes['BLUE'] = '\33[34m'
            cls._codes['VIOLET'] = '\33[35m'
            cls._codes['CYAN'] = '\33[36m'
            cls._codes['WHITE'] = '\33[37m'

            cls._codes['BG_RED'] = '\33[41m'
            cls._codes['BG_GREEN'] = '\33[42m'
            cls._codes['BG_YELLOW'] = '\33[43m'
            cls._codes['BG_BLUE'] = '\33[44m'
            cls._codes['BG_VIOLET'] = '\33[45m'
            cls._codes['BG_CYAN'] = '\33[46m'

            cls._codes['GREY'] = '\33[90m'
            cls._codes['LT_RED'] = '\33[91m'
            cls._codes['LT_GREEN'] = '\33[92m'
            cls._codes['LT_YELLOW'] = '\33[93m'
            cls._codes['LT_BLUE'] = '\33[94m'
            cls._codes['LT_VIOLET'] = '\33[95m'
            cls._codes['LT_CYAN'] = '\33[96m'
            cls._codes['BRIGHTWHITE'] = '\33[97m'

    @classmethod
    def Wrap(cls, String, Color):
        """
        Wrap a **String** in console codes based on **Color**.
        """
        return cls.GetCode(Color) + String + cls.GetCode("END")

    @classmethod
    def Format(cls, String, StripColors=False):
        """
        Format **String** by replacing [+COLOR] and [+] with console codes.

        For example: "[+RED]Roses[+]" returns the "Roses" wrapped in red console codes.

        When **StripColors** is *True*, markups are removed without inserting console codes.
        """
        def replacement(match):
            key = match.group(1)
            if key is None:
                key = 'END'
            return ucConsoleColor.GetCode(key)
        
        def removal(match):
            return ""
        
        if cls._re_format is None:
            cls._re_format = re.compile(r'\[\+(\w+)?\]')

        if StripColors:
            return cls._re_format.sub(removal, String)
        
        return cls._re_format.sub(replacement, String)
    
    @classmethod
    def PrintTest(cls):
        """
        Prints recognized colors with color codes to the console.
        """
        cls.__init_colors()
        for code in list(cls._codes.keys()):
            if code not in ['END', 'BOLD', 'ITALIC', 'UNDERLINE']:
                print(cls.Wrap(code, code))

    def __init__(self, System=None):
        ucConsoleColor.__init_colors()
        self.system = System

    def Message(self, String):
        """
        Print a message to the console.  This message will undergo color formatting.
        """
        print(self.__sysstr() + ucConsoleColor.Format(String))

    def Warning(self, String):
        """
        Print a warning message to the console.  This message will be light red.
        """
        print(self.__sysstr() + ucConsoleColor.Wrap("[WARNING] " + String, "LT_RED"))

    def Header(self, String=None):
        """
        Print a formated header string to the console.
        """
        hs = ""
        if self.system is not None:
            hs += ucConsoleColor.Wrap(self.system, "VIOLET")
        if self.system is not None and String is not None:
            hs += ": "
        if String is not None:
            hs += ucConsoleColor.Wrap(String, "LT_VIOLET")
        print ("*** "+hs+" ***")

    def __sysstr(self, Color="BLUE", Prefix="", Postfix=": "):
        if self.system is not None:
            return Prefix+ucConsoleColor.Wrap(self.system, Color)+Postfix
        return ""
