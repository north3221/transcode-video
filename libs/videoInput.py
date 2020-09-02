import subprocess, datetime, os, configparser
import os.path as osp
from libs import inputManager as im
from libs.videoInfo import videoInfo as vi
from libs.HDRInfo import HDRInfo as hdr
from libs.checkAtmos import AtmosInfo as atmos
from libs.moviedb import movieDB as mdb

class videoInput:
	
	def __init__(self, input):
		config = configparser.ConfigParser()
		config.read('config/config.ini')
		checkMovieDB = config.getboolean('MOVIEDB','CALL_MOVIEDB')
		self.__userCheck = config.getboolean('USER_OPTION','USER_CHECK')
		print('Getting video input data')
		self.type = None
		self.path = None
		self.folder = None
		self.title = None
		self.playlist = None
		self.playlistpath = None
		self.input = None
		self.year = datetime.datetime.now().year
		self.path = im.checkDir(osp.abspath(input))		
		if self.__isBlurayFolder(input):
			self.type = im.inputType.blurayBackup
			self.folder = osp.basename(input)
			self.__setPlaylist()
			self.atmos = atmos(self.playlistpath)
		elif osp.isfile(input):
			self.type = im.inputType.videoFile
			self.folder = osp.basename(osp.abspath((osp.join(input, os.pardir, os.pardir,os.pardir))))
			self.atmos = atmos(input)
		else:
			print('You dont seem to have provided an bluray folder path, please check (', input , ')')
			exit(2)
		
		self.__setTitle()
		self.input = im.getFfmpegInput(self.type, self.path)
		self.info = vi(self.input)
		self.uhd = self.info.height == '2160'
		self.hdr = hdr(self.info)
		
		if checkMovieDB: self.__getMovieDBInfo()
		self.__userInput()
	
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
		self.title = self.folder.replace("_"," ").title()				
			
	def __isBlurayFolder(self, path):
		return osp.exists(path + "\BDMV\index.bdmv")
		
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
				if osp.isfile(self.path + '\BDMV\PLAYLIST\\' + self.playlist): self.playlistpath = self.path + '\BDMV\PLAYLIST\\' + self.playlist
		
	def __userInput(self):
		indent = '\t'
		boarder = '******************************************************'
		print (boarder)
		print('Please check these details are correct:')
		print(indent,'Title:=', indent, indent, self.title)
		print(indent,'Year:=', indent, indent, self.year)
		print(indent,'Video Stream:=', indent, self.info.vstream)
		print(indent,'Audio Stream:=', indent, self.info.astream)
		print(indent,'UHD:=', indent, indent, indent,self.uhd)
		print(indent,'HDR:=', indent, indent, indent,self.hdr.exists, '(NB Cannot be changed)')
		print(indent,'Atmos:=', indent, indent,self.atmos.exists, '(NB Cannot be changed)')
		print (boarder)
		if self.__userCheck:
			user_input = input('If you would like to change any of the above, type anything and will step through, if happy just hit enter\n')
			if not user_input == '':
				input_title = input('Input Title or hit enter to leave as "' + self.title + '"\n')
				if not input_title == '': self.title = input_title
				self.__inputYear()
				input_vs = input('Input Video Stream or hit enter to leave as "' + self.info.vstream + '"\n')
				if not input_vs == '': self.info.vstream = input_vs
				input_as = input('Input Audio Stream or hit enter to leave as "' + self.info.astream + '"\n')
				if not input_as == '': self.info.astream =input_as
				input_uhd = input('Input UHD or hit enter to leave as "' + str(self.uhd) + '"\n')
				if input_uhd.lower() in ['true', 'false']: self.uhd = input_uhd.lower() == 'true'
				print(os.name)
				os.system('cls') if os.name == 'nt' else os.system('clear')
				boarder = '******************************************************'
				print (boarder)
				print('Updated based on your inputs, now set to:')
				print(indent,'Title:=', indent, indent, self.title)
				print(indent,'Year:=', indent, indent, self.year)
				print(indent,'Video Stream:=', indent, self.info.vstream)
				print(indent,'Audio Stream:=', indent, self.info.astream)
				print(indent,'UHD:=', indent, indent, indent,self.uhd)
				print(indent,'HDR:=', indent, indent, indent,self.hdr.exists)
				print(indent,'Atmos:=', indent, indent,self.atmos.exists)
				print (boarder)
		
	def __inputYear(self):
		try:
			input_year = input('Input Year or hit enter to leave as "' + str(self.year) + '"\n')
			if not input_year == '': self.year = int(input_year)
		except ValueError:
			print('You entered and invalid year (', input_year, ') so leaving as was (', self.year,')')
			
	def __getMovieDBInfo(self):
		print('Checking Movie DB for info')
		try:
			moviedb = mdb(self.title)
			if moviedb.title == None:
				print('No Movie DB info found, leaving as set by path detection')
			else:
				print('Info found from Movie DB')
				self.title = moviedb.title
				self.year = moviedb.release_date[:4]
		except:
			print('Issue getting info from MovieDB, leaving as set by path detection')
		

