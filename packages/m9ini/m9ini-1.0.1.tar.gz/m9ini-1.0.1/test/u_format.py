import os, re, datetime

class uStringFormat:

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
            s_bytes = uStringFormat.Bytes(Bytes, ByteUnits)
        s_ms = ""
        if Seconds is not None:
            s_ms = uStringFormat.Duration(Seconds, SecUnits)
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
