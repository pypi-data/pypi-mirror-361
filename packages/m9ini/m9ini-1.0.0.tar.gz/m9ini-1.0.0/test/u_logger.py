from u_color import uConsoleColor

from enum import IntEnum
class ucLoggerLevel(IntEnum):
    DETAILS = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

class ucLogger:
    
    def __init__(self, Print:bool=True, PrintLevel:ucLoggerLevel=ucLoggerLevel.WARNING, PrintColor:bool=False):
        '''
        uLogger is super-class for other logging classes, such as uFileLogger. If used as-is, uLogger logs to the console.
        - *Print*: print to console
        - *PrintLevel*: only print message at or above this level
        - *PrintColor*: include color codes using **uConsoleColor**
        '''
        self.header_char = '='
        self.header_len = 69
        self.subheader_char = '-'
        self.write_level = ucLoggerLevel.INFO
        self.print = Print
        self.print_level = PrintLevel
        self.print_color = PrintColor
        self.ResetCounts()
    
    def __del__(self):
        pass

    def SetWriteLevel(self, Level:ucLoggerLevel):
        '''
        Only write enteries at or above **Level**.
        '''
        self.write_level = Level

    def WriteBlank(self, Level=ucLoggerLevel.INFO):
        '''
        Writes a blank line.
        '''
        self.WriteLine("", Level)

    def WriteLine(self, Line, Level=ucLoggerLevel.INFO):
        '''
        Writes a **Line** of the specified **Level**.

        The default level is *INFO*.
        '''
        if Level==ucLoggerLevel.WARNING:
            self.count_warn += 1

        if Level==ucLoggerLevel.ERROR:
            self.count_error += 1

        if self.print and Level>=self.print_level:
            print (uConsoleColor.Format(Line, not self.print_color))

        if Level >= self.write_level:
            self.imp_writeline(uConsoleColor.Format(Line, True), Level)
        
    def WriteDetails(self, Line):
        '''
        Writes a **Line** at level *DETAILS*.  *DETAILS* is the lowest level.
        '''
        self.WriteLine(f"[+GREY]{Line}[+]", ucLoggerLevel.DETAILS)
        
    def WriteWarning(self, Line):
        '''
        Writes a **Line** at level *WARNING*.
        '''
        self.WriteLine(f"[+YELLOW]{Line}[+]", ucLoggerLevel.WARNING)
        
    def WriteError(self, Line):
        '''
        Writes a **Line** at level *ERROR*.
        '''
        self.WriteLine(f"[+LT_RED]{Line}[+]", ucLoggerLevel.ERROR)

    # Printing

    def SetPrint(self, Print:bool=True, Level:ucLoggerLevel=None, Color:bool=None):
        '''
        Sets console printing to **Print**.

        When **Level** is not *None*, changes level setting for console logging.

        If **Color** is not *None*, changes color setting for console logging.
        '''
        self.print = Print
        if Level is not None:
            self.print_level = Level
        if Color is not None:
            self.print_color = Color
        
    def SetPrintLevel(self, PrintLevel:ucLoggerLevel):
        '''
        Sets the color setting for console logging.
        '''
        self.print_level = PrintLevel

    # Counts
        
    def ResetCounts (self):
        '''
        Resets warning and error counts.
        '''
        self.count_warn = 0
        self.count_error = 0

    def GetWarningCount (self)->int:
        '''
        Returns number of warnings logged.
        '''
        return self.count_warn

    def GetErrorCount (self)->int:
        '''
        Returns number of errors logged.
        '''
        return self.count_error

    # Standard formatting

    def ConfigFormat(self, HeaderChar:str=None, HeaderLen:str=None, SubheaderChar:str=None):
        '''
        Change characters used for logging headers.
        '''
        if HeaderChar:
            self.header_char = HeaderChar
        if HeaderLen:
            self.header_len = HeaderLen
        if SubheaderChar:
            self.subheader_char = SubheaderChar

    def WriteHeader(self, Title):
        self.imp_write_header(self.header_char, self.header_len, Title)

    def WriteSubHeader(self, Title):
        self.imp_write_subheader(self.subheader_char, self.header_len, Title)

    def WriteSubDivider(self, SubheaderChar=None, PadAbove=False, PadBelow=False, Padding=False):
        if SubheaderChar is None:
            SubheaderChar = self.subheader_char
        if Padding:
            PadAbove = True
            PadBelow = True
        self.imp_write_subdivider(SubheaderChar, self.header_len, PadAbove, PadBelow)

    # Implementation methods

    def __calc_remaining(self, in_title, in_header_len, in_buffer):
        calc = in_header_len - in_buffer - len(in_title)
        if calc < 0:
            calc = 0
        return calc
    
    def imp_writeline(self, in_line, in_level):
        pass

    def imp_writenewline(self):
        pass

    def imp_write_header(self, in_header_char, in_header_len, in_title):
        self.WriteLine(in_header_char * in_header_len)
        self.WriteLine(in_header_char * 3 + " " + in_title)
        self.WriteLine(in_header_char * in_header_len)

    def imp_write_subheader(self, in_header_char, in_header_len, in_title):
        self.WriteLine(in_header_char * 3 + " " + in_title + " " + in_header_char * self.__calc_remaining(in_title, in_header_len, 5))

    def imp_write_subdivider(self, in_header_char, in_header_len, in_pad_above, in_pad_below):
        if in_pad_above:
            self.WriteBlank()
        self.WriteLine(in_header_char * in_header_len)
        if in_pad_below:
            self.WriteBlank()

import os

from u_format import uStringFormat
from u_folder import uFolder

class ucFileLogger(ucLogger):
    def __init__(self, Filepath:str=None, Print:bool=True, PrintLevel:ucLoggerLevel=ucLoggerLevel.WARNING, PrintColor:bool=False):
        '''
        If **Filepath** is not None, begins logging to the specified path.

        **Filepath** supports **uStringFormat** replacements like **{YMD}** and **{TSM}**.
        '''
        super().__init__(Print, PrintLevel, PrintColor)
        self.filepath = None
        if Filepath is not None:
            self.Start (Filepath)

    def __del__(self):
        super().__del__()
        if self.file is not None:
            self.file.close()
            
    def Start(self, Filepath:str):
        '''
        STarts logging to **Filepath**.

        **Filepath** supports **uStringFormat** replacements like **{YMD}** and **{TSM}**.
        '''
        self.filepath = uStringFormat.String (Filepath)
        head, _ = os.path.split(self.filepath)
        uFolder.ConfirmFolder(head)
        self.file = open(self.filepath, 'a')

    def GetFilepath(self)->str:
        '''
        Returns path to logfile.
        '''
        return self.filepath
        
    def imp_writeline(self, in_line, in_level):
        decoration = ""
        if in_level == ucLoggerLevel.DETAILS:
            decoration = ".."
        elif in_level == ucLoggerLevel.WARNING:
            decoration = "*WARN: "
        elif in_level == ucLoggerLevel.ERROR:
            decoration = "*ERROR: "
        line = self.__line_prefix () + decoration + in_line
        
        if self.file is not None:
            try:
                self.file.write (line + "\n")
            except:
                self.file.write (str(line.encode('utf8')) + "\n")
            self.file.flush()

    def imp_writenewline(self):
        if self.file is not None:
            self.file.write ("\n")
            self.file.flush()
            
    def __line_prefix(self):
        return uStringFormat.String ("{LTS} ")
