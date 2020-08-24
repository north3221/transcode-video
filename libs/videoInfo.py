import subprocess

class videoInfo:

	def __init__(self, input):
		print('Analyzing video..')
		self.vstream = 'v:0'
		self.astream = 'a:0'
		self.__initInfo(input)

	def __initInfo(self, input):
		ffprobe_cmd = 'ffprobe -loglevel quiet -probesize 4096M -analyzeduration 4096M -prefix -unit -show_streams -select_streams v:0 -show_frames -read_intervals "%+#1" -i ' + input
		try:
			output = subprocess.check_output(ffprobe_cmd, stderr=subprocess.STDOUT)
		except Exception as e:			
			outpute = e.output
			print (outpute)
			exit()
		output = output.decode().split('\n')
		for line in output:
			if '=' in line and not ':' in line:
				p = line.split("=", 1)
				exec("self." + p[0] + " = '" + p[1].replace('\r','') + "'")
		
		
	# Adding in a safer get() method. Can call attributes directly but will error if doesnt exist, so this is a safe way to get attribute
	def get(self, index):
		return getattr(self, index, None)