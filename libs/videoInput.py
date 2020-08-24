import subprocess, datetime
import os.path as osp
from libs import inputManager as im
from libs.videoInfo import videoInfo as vi
from libs.HDRInfo import HDRInfo as hdr
from libs.checkAtmos import AtmosInfo as atmos

class videoInput:
	
	def __init__(self, input):
		print('Getting video input data')
		self.type = None
		self.path = None
		self.folder = None
		self.title = None
		self.playlist = None
		self.playlistpath = None
		self.input = None
		self.year = datetime.datetime.now().year
				
		if self.__isBlurayFolder(input):
			self.type = im.inputType.blurayBackup
			self.path = im.checkDir(osp.abspath(input))
			self.folder = osp.basename(input)
			self.__setTitle()
			self.__setPlaylist()
		else:
			print('You dont seem to have provided an bluray folder path, please check (', input , ')')
			exit(2)
		
		self.input = im.getFfmpegInput(self.type, self.path)
		self.info = vi(self.input)
		self.uhd = self.info.height == '2160'
		self.hdr = hdr(self.info)
		self.atmos = atmos(self.playlistpath)
		self.__userCheck()
	
	@property
	def title(self):
		return self.__title
	
	@title.setter
	def title(self, val):
		self.__title = val
		
	@property
	def ofilename(self):
		return self.__title + '(' + str(self.year) + ')'
	
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
		
	def __userCheck(self):
		indent = '\t'
		boarder = '******************************************************'
		print (boarder)
		print('Please check these details are correct:')
		print(indent,'Title:=', indent, indent, self.title)
		print(indent,'Year:=', indent, indent, self.year)
		print(indent,'Video Stream:=', indent, self.info.vstream)
		print(indent,'Audio Stream:=', indent, self.info.astream)
		print(indent,'UHD:=', indent, indent, indent,self.uhd)
		print(indent,'HDR:=', indent, indent, indent,self.hdr.exists)
		print(indent,'Atmos:=', indent, indent,self.atmos.exists)
		print (boarder)
		user_input = input('If you would like to change any of the above, type anything and will step through, if happy just hit enter\n')
		if not user_input == '':
			input_title = input('Input Title or hit enter to leave as "' + self.title + '"\n')
			if not input_title == '': self.title = input_title
			self.__inputYear()
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
			
		
		
				
