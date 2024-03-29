import subprocess, datetime, os, configparser
import os.path as osp
try:
    from libs import inputManager as im
    from libs.videoInfo import videoInfo as vi
    from libs.HDRInfo import HDRInfo as hdr
    from libs.checkAtmos import AtmosInfo as atmos
    from libs.moviedb import movieDB as mdb
except ImportError:
    import inputManager as im
    from videoInfo import videoInfo as vi
    from HDRInfo import HDRInfo as hdr
    from checkAtmos import AtmosInfo as atmos
    from moviedb import movieDB as mdb
    

class videoInput:
    
    def __init__(self, input):
        print('Getting video input data..')
        self.__initVars()
        self.type = None
        self.path = None
        self.folder = None
        self.__title = None
        self.playlist = None
        self.playlistpath = None
        self.input = None
        self.year = datetime.datetime.now().year
        self.path = im.checkDir(osp.abspath(input))     
        if self.__isBlurayFolder(input):
            print('Bluray folder found')
            self.type = im.inputType.blurayBackup
            self.folder = osp.basename(input)
            self.__setPlaylist()
            self.atmos = atmos(self.playlistpath)
        elif self.__isBlurayFolder(osp.abspath((osp.join(input, os.pardir, os.pardir, os.pardir)))):
            print('File within Bluray folder found')
            self.type = im.inputType.videoFile
            self.folder = osp.basename(osp.abspath((osp.join(input, os.pardir, os.pardir, os.pardir))))
            self.atmos = atmos(input)
        elif osp.isfile(input):
            print('File found')
            self.type = im.inputType.videoFile
            self.folder = osp.basename(osp.abspath((osp.join(input, os.pardir))))
            self.atmos = atmos(input)
        else:
            print('You dont seem to have provided an bluray folder path, please check (', input , ')')
            exit(2)
        self.__setTitle()
        self.input = im.getFfmpegInput(self.type, self.path)
        self.info = vi(self.input)
        self.uhd = self.info.height == '2160'
        self.hdr = hdr(self.info)
        
        if self.__checkMovieDB: self.__getMovieDBInfo(self.__title)
        self.__userInput()
        
    def __initVars(self):
        config = configparser.ConfigParser()
        config.read(osp.realpath(osp.join(osp.dirname(osp.abspath(__file__)),'../config/config.ini')))
        self.__checkMovieDB = config.getboolean('MOVIEDB','CALL_MOVIEDB')
        self.__x264_override = config.getboolean('MOVIEDB','X264_TUNE_OVERRIDE')
        self.__userCheck = config.getboolean('USER_OPTION','USER_CHECK')
        self.__userCheckConf = config.getint('USER_OPTION','USER_CHECK_CONFIDENCE')
        self.x264_tune = config.get('HD_OPTIONAL','X264_TUNE')
    
    @property
    def title(self):
        return self.__title
    
    @title.setter
    def title(self, val):
        self.__title = val
        
    @property
    def ofilename(self):
        return self.__title + ' (' + str(self.year) + ')'
    
    def __setTitle(self):
        self.__title = self.folder.replace("_"," ").title()               
            
    def __isBlurayFolder(self, path) -> bool:
        path = path.strip('"') + '\BDMV\index.bdmv'
        return osp.exists(path)
        
    def __setPlaylist(self):
        cmdFfmpeg = 'ffmpeg -i bluray:{blurayFolder}'.format(blurayFolder=self.path)
        try:
            output = subprocess.check_output(cmdFfmpeg, stderr=subprocess.STDOUT)
        except Exception as e:          
            output = e.output
        output = output.decode().split('\n')
        for line in output:
            if "selected" in line:
                splitline = line.split()
                self.playlist = splitline[splitline.index("selected") + 1]
                pl_check = self.path.strip('"') + '\BDMV\PLAYLIST\\' + self.playlist
                if osp.isfile(pl_check): self.playlistpath = pl_check
        
    def __userInput(self):
        self.__printInfo()
        if self.__userCheck:
            user_input = input('If you would like to change any of the above, type anything and will step through, if happy just hit enter\n')
            if not user_input == '':
                os.system('cls') if os.name == 'nt' else os.system('clear')
                self.__printInfo('Updated based on your inputs, now set to')
                input_search = input('Input new Movie DB Search or hit enter to input manually\n')
                if input_search == '': 
                    input_title = input('Input Title or hit enter to leave as "' + self.__title + '"\n')
                    if not input_title == '': self.__title = input_title
                    self.__inputYear()
                    input_vs = input('Input Video Stream or hit enter to leave as "' + self.info.vstream + '"\n')
                    if not input_vs == '': self.info.vstream = input_vs
                    input_as = input('Input Audio Stream or hit enter to leave as "' + self.info.astream + '"\n')
                    if not input_as == '': self.info.astream =input_as
                    input_uhd = input('Input UHD or hit enter to leave as "' + str(self.uhd) + '"\n')
                    if input_uhd.lower() in ['true', 'false']: self.uhd = input_uhd.lower() == 'true'
                else:
                    self.__getMovieDBInfo(input_search, True)
                    self.__userInput()
                    
    
    def __printInfo(self, header='Please check these details are correct'):
        indent = '\t'
        boarder = '******************************************************'
        print (boarder)
        print(header, ':')
        print(indent,'Title:=', indent, indent, self.__title)
        print(indent,'Year:=', indent, indent, self.year)
        print(indent,'Video Stream:=', indent, self.info.vstream)
        print(indent,'Audio Stream:=', indent, self.info.astream)
        print(indent,'UHD:=', indent, indent, indent,self.uhd)
        print(indent,'HDR:=', indent, indent, indent,self.hdr.exists, '(NB Cannot be changed)')
        print(indent,'Atmos:=', indent, indent,self.atmos.exists, '(NB Cannot be changed)')
        print(indent,'x264 Tune:=', indent, indent,self.x264_tune, '(NB Cannot be changed)')
        print (boarder)

    
    def __inputYear(self):
        try:
            input_year = input('Input Year or hit enter to leave as "' + str(self.year) + '"\n')
            if not input_year == '': self.year = int(input_year)
        except ValueError:
            print('You entered and invalid year (', input_year, ') so leaving as was (', self.year,')')
            
    def __getMovieDBInfo(self, search, self_check=False):
        try:
            moviedb = mdb(search, self_check)
            if moviedb.title == None:
                print('No Movie DB info found, leaving as set by path detection and ensuring user validation if user confidence not zero')
                if self.__userCheckConf > 0: self.__userCheck = True
            else:
                self.__title = moviedb.title
                self.year = moviedb.release_date[:4]
                if self.__x264_override and not moviedb.x264_tune == None: self.x264_tune = moviedb.x264_tune
                if not self.__userCheck and moviedb.match <= self.__userCheckConf: self.__userCheck = True
                self.mdb = moviedb
        except:
            print('Issue getting info from MovieDB, leaving as set by path detection and ensuring user validation if user confidence not zero')
            if self.__userCheckConf > 0: self.__userCheck = True
        

