import sys, getopt, shutil, libs.fileInfo as fi
from libs.videoInput import videoInput as vinput
from os import path

import configparser
import subprocess, os

############### CONFIG ##########################
config = configparser.ConfigParser()
config.read('config.ini')
opts = {}
for section in config.sections():
	for key, val in config.items(section):
		try: # Try int
			exec('opts["' + key + '"] = ' + val)
		except: # So str
			exec('opts["' + key + '"] = "' + val + '"')	
			# Try bolean
			if val.lower() in ('true', 'false'): exec('opts["' + key + '"] = ' + val.title())
output_path = fi.checkDir(opts['output_path'])
log_path = fi.checkDir(opts['log_path'])
temp_path = fi.checkDir(opts['temp_path'])
############# END CONFIG ########################
videoInput = None
sample = False
def main():
	global sample
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hi:s",["help","input=","sample"])
		if len(opts) == 0:
			print('No Input provided')
			__usage(2)
	except getopt.GetoptError:
		print ('Invalid input ', sys.argv[1:] )
		__usage(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			__usage(0)
		elif opt in ("-i", "--input"):
			input = arg
		elif opt in ("-s", "--sample"):
			sample = True
	
	__loadVideoInput(input)
	__runTranscode()

def __loadVideoInput(inputfile):
	global videoInput
	videoInput = vinput(inputfile)
	
def __runTranscode():
	# Idealy find a way to pass StingIO file direct to ffmpeg...? but for now
	global metadata 
	metadata = path.join(temp_path, videoInput.title + '.met')
	print(metadata)
	with open(metadata, 'w') as met:
		print(videoInput.info.chapters.read(), file=met)
	cmd = __createFFMPEGcmd()
	with open(log_path + videoInput.ofilename + '.cmd.log', "w") as log_file:
		print (cmd, file=log_file)
	print ('Running transcode job')
	with open(log_path + videoInput.ofilename + '.transcode.log', 'w') as log_file:
		subprocess.call(cmd, stderr=subprocess.STDOUT, stdout=log_file)
	print('Process complete')
	shutil.rmtree(temp_path)

def __createFFMPEGcmd():
	cmd = []
	cmd.append(__baseFFMPEGcmd())
	cmd.append(__hdFFMPEGcmd())
	if videoInput.uhd: cmd.append(__uhdFFMPEGcmd())
	return ' '.join(cmd)
	
	
def __baseFFMPEGcmd():
	cmd = ['ffmpeg ' + opts['ffmpeg_options']]
	cmd.append('-loglevel ' + opts['ffmpeg_loglevel'])
	cmd.append('-probesize ' + opts['ffmpeg_prob_anal'])
	cmd.append('-analyzeduration ' + opts['ffmpeg_prob_anal'])
	cmd.append('-forced_subs_only ' + str(opts['ffmpeg_forced_subs_only']))
	# Seems to be an issue having metadata as second input, seeems to only work on first?
	cmd.append('-i "' + metadata + '"')
	if sample: cmd.append(opts['sample_time'])
	cmd.append('-i ' + videoInput.input)
	
	return ' '.join(cmd)

def __hdFFMPEGcmd():
	cmd = ['-map_metadata 0 -map 1:' + videoInput.info.vstream]
	if videoInput.hdr.exists: cmd.append(videoInput.hdr.sdrmap)
	cmd.append('-c:v ' + opts['hd_codec'])
	if not opts['x264_level'] == '': cmd.append('-level:v ' +  str(opts['x264_level'])) 
	cmd.append('-crf ' + str(opts['hd_crf']))
	if not opts['hd_maxrate'] == '':
		cmd.append('-maxrate ' + str(opts['hd_maxrate']) + 'k')
		cmd.append('-bufsize ' + str(opts['hd_maxrate']*3) + 'k')
	cmd.append('-preset ' + opts['hd_preset'])
	if not opts['x264_tune'] == '': cmd.append('-tune ' + opts['x264_tune'])
	cmd.append('-s ' + opts['hd_size'])
	cmd.append('-pix_fmt ' + opts['hd_pix_fmt'])
	
	aos = '0'
	if opts['add_stereo']:
		if opts['stereo_primary']:
			cmd.append('-filter_complex "[1:' + videoInput.info.astream + ']volume=2.5:precision=fixed[a]" -map [a] -c:a:' + aos + ' aac -b:a:' + aos + ' 320k -ac:a:' + aos + ' 2 -metadata:s:a:' + aos + ' title="Stereo" -metadata:s:a:' + aos + ' handler="Stereo"')
			aos = '1'
		else:
			cmd.append('-map 1:' + videoInput.info.astream + ' -c:a:' + aos + ' eac3 -b:a:' + aos + ' 640k -metadata:s:a:' + aos + ' title="Surround 5.1" -metadata:s:a:' + aos + ' handler="Surround 5.1"')
			aos = '1'
			cmd.append('-filter_complex "[1:' + videoInput.info.astream + ']volume=2.5:precision=fixed[a]" -map [a] -c:a:' + aos + ' aac -b:a:' + aos + ' 320k -ac:a:' + aos + ' 2 -metadata:s:a:' + aos + ' title="Stereo" -metadata:s:a:' + aos + ' handler="Stereo"')
	else:
		cmd.append('-map 1:' + videoInput.info.astream + ' -c:a:' + aos + ' eac3 -b:a:' + aos + ' 640k -metadata:s:a:' + aos + ' title="Surround 5.1" -metadata:s:a:' + aos + ' handler="Surround 5.1"')
	cmd.append('-metadata:s:a language=eng')
	cmd.append('-metadata title="' + videoInput.title + '" -metadata date="' + str(videoInput.year) + '"')
	
	output = '"' + output_path + videoInput.ofilename + '.'
	if videoInput.hdr.exists: output = output + 'SDR.'
	if sample: output = output + 'sample.'
	cmd.append(output + opts['hd_ext'] + '" -y')
	return ' '.join(cmd)

def __uhdFFMPEGcmd():
	cmd = ['-map_metadata 0 -map 1:' + videoInput.info.vstream + ' -c:v libx265']
	cmd.append('-preset ' +  opts['uhd_preset'])
	if not opts['uhd_pix_fmt'] == '': videoInput.info.pix_fmt = opts['uhd_pix_fmt']
	cmd.append('-pix_fmt ' + videoInput.info.pix_fmt + ' -x265-params')
	params = 'crf=' + str(opts['uhd_crf'])
	if not opts['uhd_maxrate'] == '' :
		params = params + ':vbv-maxrate=' + str(opts['uhd_maxrate'])
		params = params + ':vbv-bufsize=' + str(opts['uhd_maxrate']*3)
	if videoInput.hdr.exists: params = params + ':' + videoInput.hdr.params
	cmd.append(params)
	aos = '0'
	if videoInput.atmos.exists:
		cmd.append('-map 1:' + videoInput.info.astream + ' -c:a:' + aos + ' ' + opts['uhd_acodec'] + ' -b:a:' + aos + ' 640k') 
		cmd.append('-metadata:s:a:' + aos + ' title="Surround 5.1" -metadata:s:a:' + aos + ' handler="Surround 5.1"')
		aos = '1'
	# copy audio, either its not atmos and just a straight copy to be the audio stream or it is Atmos so this is copying atmos to second stream
	cmd.append('-map 1:' + videoInput.info.astream + ' -c:a:' + aos + ' copy -max_muxing_queue_size 4096')
	if videoInput.atmos.exists: cmd.append('-metadata:s:a:' + aos + ' title="Dolby Atmos" -metadata:s:a:' + aos + ' handler="Dolby Atmos"')
	cmd.append('-metadata:s:a language=eng')
	cmd.append('-metadata title="' + videoInput.title + '" -metadata year="' + str(videoInput.year) + '"')
	
	output = '"' + output_path + videoInput.ofilename + '.UHD.'
	if videoInput.hdr.exists: output = output + 'HDR.'
	if sample: output = output + 'sample.'
	cmd.append(output + opts['uhd_ext'] + '" -y')
	
	return ' '.join(cmd)
	
	
def __usage(exit_code):
	script = os.path.basename(__file__)
	print('Correct Usage:')
	print (script, '-h[--help]  Show this help')
	print (script, '-i[--input] <inputfile> -s[--sample] (optional)')
	print ('NB sample time is a setting in config.ini')
	exit(exit_code)
if __name__ == "__main__":
    main()
