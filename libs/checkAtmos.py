import subprocess

class AtmosInfo:

	def __init__(self, playlist):
		print('Checking for Dolby Atmos audio....')
		self.__setAtmos(playlist)
			
	def __setAtmos(self, playlist):
		delim = '/'
		cmdMediaIffo = 'mediainfo --Inform="Audio;%Format_Commercial_IfAny%' + delim + '" ' + playlist
		try:
			output = subprocess.check_output(cmdMediaIffo, stderr=subprocess.STDOUT)
		except Exception as e:			
			outpute = e.output
			print (outpute)
			exit()
		output = output.decode("utf-8")
		self.exists = 'Atmos' in output
		if self.exists: self.stream = [i for i, s in enumerate(output.split('/')) if 'Atmos' in s][0]
			
		
		