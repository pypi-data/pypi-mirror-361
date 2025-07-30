
import os,shutil
import fnmatch

class uFolder:

    def __init__(self, Folderpath, Create=True):
        self.folderpath = Folderpath

        if Create:
            uFolder.ConfirmFolder(Folderpath, True)

    def Exists(self)->bool:
        return self.folderpath
    
    def GetFolderpath(self)->str:
        return self.folderpath

    @staticmethod
    def ConfirmFolder(Folderpath, Create=True):
        '''
        Confirms if the folder exists, creating if **Create** is *True*.

        Returns *True* if the folder exists.
        '''
        try:
            if os.path.isdir(Folderpath):
                return True

            if Create:
                os.makedirs(Folderpath)
                return True

            return False
            
        except:
            return False
        
    _temp_folders = []

    @classmethod
    def CreateTempFolder(cls, Rootfolder, Namemask="Temp-{:03d}"):
        '''
        Creates a temporary folder under **Rootfolder**, and returns a folder path.

        You may specify a **Namemask** that contains {:03d} for a custom folder name.

        Returns *None* if there is not a unique name because there are 1000 temp folders already.

        Returns *False* if unable to create the folder.
        '''
        try:
            index = 1
            ret_folder = None
            while ret_folder is None and index<1000:
                try_folder = os.path.join(Rootfolder, Namemask.format(index))
                if os.path.exists(try_folder) is False:
                    if uFolder.ConfirmFolder(try_folder) is True:
                        ret_folder = try_folder

                index += 1

            if ret_folder is None:
                return False
            
            cls._temp_folders.append(ret_folder)

            return ret_folder
            
        except:
            return False
        
    @classmethod
    def DestroyTempFolders(cls):
        '''
        Removes temporary folders created by **uFolder**
        
        Returns (*count*, [*folder*]) where *count* is the number of folders destroyed, and [*folder*] is a list of folders that failed to destroy.
        '''
        count = 0
        failed = []
        for folder in cls._temp_folders:
            ret = uFolder.DestroyFolder(folder)
            if ret is True:
                count += 1
            elif ret is False:
                failed.append(folder)

        cls._temp_folders = []
        return (count, failed)

    @staticmethod
    def FindFiles(Folderpath:str, Recurse:bool=False, Files:bool=True, Folders:bool=False, Match:str="*"):
        '''
        Locates files at the specified **Folderpath**.
        - **Recurse**: recurse folders
        - **Files**: result will include files
        - **Folders**: result will include folders
        - **Match**: a match string

        Returns a list of (*name*, *path*).
        '''
        ret_files = []
        if Recurse:
            for root, dirs, files in os.walk(Folderpath):
                if Files:
                    for file in files:
                        if fnmatch.fnmatch(file, Match):
                            ret_files.append((file, root))
                if Folders:
                    for file in dirs:
                        if fnmatch.fnmatch(file, Match):
                            ret_files.append((file, root))
        else:
            for file in os.listdir(Folderpath):
                if fnmatch.fnmatch(file, Match):
                    filepath = os.path.join(Folderpath, file)
                    if (Files and os.path.isfile (filepath)) or (Folders and os.path.isdir (filepath)):
                        ret_files.append((file, Folderpath))

        return ret_files

    @staticmethod
    def OrganizeFilesByPath(Files):
        '''
        Reorganizes a list of (*name*, *path*) returned by FindFiles() by folder path.

        Returns a list of (*folderpath*, [*file1*, *file2*, ..]).
        '''
        org = {}
        for file in Files:
            name = file[0]
            path = file[1]
            if path not in org:
                org [path] = [name]
            else:
                org [path].append(name)

        ret_files = []
        for key in org.keys():
            ret_files.append((key, org[key]))

        return ret_files

    @staticmethod
    def DestroyEmptyFolders(Folderpath):
        '''
        Recursively destroys empty folders, starting at (and including) **Folderpath**.

        Returns a list of destroyed folders.
        '''
        folders = []
        try:
            if os.path.isdir(Folderpath):
                subfolder_folders = []
                for file in os.listdir(Folderpath):
                    filepath = os.path.join(Folderpath, file)
                    if os.path.isdir(filepath):
                        ret_subfolders = uFolder.DestroyEmptyFolders(filepath)
                        subfolder_folders.extend(ret_subfolders)

                deleted_thisfolder = False
                if len(os.listdir(Folderpath))==0:
                    deleted_thisfolder = uFolder.DestroyFolder(Folderpath) is True

                if deleted_thisfolder:
                    folders = [Folderpath]
                else:
                    folders = subfolder_folders
        except:
            pass

        return folders
    
    @staticmethod
    def DestroyFolder(Folderpath):
        '''
        Completely removes **Folderpath** folder, include any contents.

        Returns :
        - *True*: folder was destroyed
        - *None*: no action taken (**Folderpath** is not a folder)
        - *False*: failed
        '''
        try:
            if os.path.isdir(Folderpath):
                shutil.rmtree(Folderpath)
                return not os.path.isdir(Folderpath)
            
            return None
        except:
            return False
        
    @staticmethod
    def TrimOldFiles(Folderpath, Match="*", KeepCount=20)->list:
        '''
        Deletes older files in **Folderpath** that **Match** a file match, but retaining the **KeepCount** latest files.

        Returns a list of filepaths removed.
        '''
        clean = []
        organize = []
        files = uFolder.FindFiles(Folderpath, Match=Match)
        for file in files:
            filepath = os.path.join(file[1], file[0])
            organize.append((os.path.getmtime(filepath), filepath))

        organize = [string for _, string in sorted(organize, key=lambda x: x[0])]
        if len(organize)>KeepCount:
            clean = organize[:len(organize)-KeepCount]

        for cfile in clean:
            os.remove(cfile)
        
        return clean
