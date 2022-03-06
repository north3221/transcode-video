import sys, getopt, shutil, configparser, os, subprocess 
from libs import fileInfo as fi
from libs.videoInput import videoInput as vinput
from libs.subs import subsBackup
from os import path
############### CONFIG ##########################
config = configparser.ConfigParser()
config.read(os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'config/config.ini')))
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
        inpts, args = getopt.getopt(sys.argv[1:],"hi:s",["help","input=","sample"])
        if len(inpts) == 0:
            print('No Input provided')
            __usage(2)
    except getopt.GetoptError:
        print ('Invalid input ', sys.argv[1:] )
        __usage(2)
    for opt, arg in inpts:
        if opt in ("-h", "--help"):
            __usage(0)
        elif opt in ("-i", "--input"):
            input = arg
        elif opt in ("-s", "--sample"):
            sample = True
    
    __loadVideoInput(input)
    __runTranscode()
    __moveOutput()
    if opts['backup_subs']:
        subsBackup(videoInput)


def __loadVideoInput(inputfile):
    global videoInput
    videoInput = vinput(inputfile)
    
def __runTranscode():
    # Ideally find a way to pass StingIO file direct to ffmpeg...? but for now
    global metadata 
    metadata = path.join(temp_path, videoInput.title + '.met')
    with open(metadata, 'w') as met:
        print(videoInput.info.chapters.read(), file=met)
    cmd = __createFFMPEGcmd()
    with open(log_path + videoInput.ofilename + '.cmd.log', "w") as log_file:
        print (cmd, file=log_file)
    print ('Running transcode job')
    with open(log_path + videoInput.ofilename + '.transcode.log', 'w') as log_file:
        subprocess.call(cmd, stderr=subprocess.STDOUT, stdout=log_file, shell=True)
    print('Process complete')
    if opts['delete_temp']: shutil.rmtree(temp_path)

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
    # Seems to be an issue having metadata as second input, seems to only work on first?
    cmd.append('-i "' + metadata + '"')
    if sample: cmd.append(opts['sample_time'])
    cmd.append('-forced_subs_only ' + str(opts['ffmpeg_forced_subs_only']))
    cmd.append('-hwaccel cuda')
    cmd.append('-i ' + videoInput.input)
    
    return ' '.join(cmd)

def __hdFFMPEGcmd():
    cmd = ['-map_metadata 0']
    # TODO wont work, but gone with subs backup instead and adding as subs track instead of buring on
    if opts['burn_subs']:
        cmd.append('-filter_complex " [1:' + videoInput.info.vstream + ']pad=1920:1080[main];[main][1:s:' + str(opts['sub_stream']) + ']overlay[v]" -map [v]')
    else:
        cmd.append('-map 1:' + videoInput.info.vstream)
    if videoInput.hdr.exists: cmd.append(videoInput.hdr.sdrmap)
    cmd.append('-c:v ' + opts['hd_codec'])
    if not opts['x264_level'] == '': cmd.append('-level:v ' +  str(opts['x264_level'])) 
    cmd.append('-crf ' + str(opts['hd_crf']))
    if not opts['hd_maxrate'] == '':
        cmd.append('-maxrate ' + str(opts['hd_maxrate']) + 'k')
        cmd.append('-bufsize ' + str(opts['hd_maxrate']*3) + 'k')
    cmd.append('-preset ' + opts['hd_preset'])
    if not videoInput.x264_tune == '': cmd.append('-tune ' + videoInput.x264_tune)
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
    
    
    global hd_output
    hd_output = output_path + videoInput.ofilename + '.'
    if videoInput.hdr.exists: hd_output = hd_output + 'SDR.'
    if sample: hd_output = hd_output + 'sample.'
    hd_output = hd_output + opts['hd_ext']
    cmd.append('"' + hd_output  + '" -y')
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
    # Add audio based on user codec choice
    cmd.append('-map 1:' + videoInput.info.astream + ' -c:a:0 ' + opts['uhd_acodec'] + ' -b:a:0 640k') 
    cmd.append('-metadata:s:a:0 title="Surround 5.1" -metadata:s:a:0 handler="Surround 5.1"')
    
    # If copy atmos is set by user and atmos exists copy it
    if videoInput.atmos.exists and opts['uhd_copy_atmos']:
        cmd.append('-map 1:' + videoInput.info.astream + ' -c:a:1 copy -max_muxing_queue_size 4096')
        cmd.append('-metadata:s:a:1 title="Dolby Atmos" -metadata:s:a:1 handler="Dolby Atmos"')
    
    cmd.append('-metadata:s:a language=eng')
    cmd.append('-metadata title="' + videoInput.title + '" -metadata year="' + str(videoInput.year) + '"')
    
    global uhd_output
    uhd_output = output_path + videoInput.ofilename + '.UHD.'
    if videoInput.hdr.exists: uhd_output = uhd_output + 'HDR.'
    if sample: uhd_output = uhd_output + 'sample.'
    uhd_output = uhd_output + opts['uhd_ext']
    cmd.append('"' + uhd_output  + '" -y')
    
    return ' '.join(cmd)

def __moveOutput():
    if opts['hd_move_output']:
        hd_folder = videoInput.mdb.__dict__[opts['hd_folder_var']] if opts['hd_folder_var'] else ''
        hd_move_to = os.path.realpath(os.path.join(opts['hd_base_dir'],hd_folder))
        print('Moving HD to:= ', hd_move_to)
        try:
            fi.checkDir(hd_move_to)
            shutil.move(hd_output, hd_move_to)
            with open(log_path + videoInput.ofilename + '.cmd.log', "a") as log_file:
                print('HD version moved to:= ', hd_move_to, file=log_file)
        except:
            print('something went wrong trying to move it')
    if opts['uhd_move_output'] and videoInput.uhd:
        uhd_folder = videoInput.mdb.__dict__[opts['uhd_folder_var']] if opts['uhd_folder_var'] else ''
        uhd_move_to = os.path.realpath(os.path.join(opts['uhd_base_dir'],uhd_folder))
        print('Moving UHD to:= ', uhd_move_to)
        try:
            fi.checkDir(uhd_move_to)
            shutil.move(uhd_output, uhd_move_to)
            with open(log_path + videoInput.ofilename + '.cmd.log', "a") as log_file:
                print('UHD version moved to:= ', uhd_move_to, file=log_file)
        except:
            print('something went wrong trying to move it')
    
def __usage(exit_code):
    script = os.path.basename(__file__)
    print('Correct Usage:')
    print (script, '-h[--help]  Show this help')
    print (script, '-i[--input] <inputfile> -s[--sample] (optional)')
    print ('NB sample time is a setting in config.ini')
    exit(exit_code)
if __name__ == "__main__":
    main()
