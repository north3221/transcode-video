import os, configparser, getopt, sys, subprocess, shutil
try:
    from libs import videoInput as vi
    from libs import fileInfo as fi
except ImportError:
    import videoInput as vi
    import fileInfo as fi

config = configparser.ConfigParser()
base_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__))+'\\..\\')
config_path = os.path.realpath(os.path.join(base_path,'config/config.ini'))
config.read(config_path)
subs_path = fi.checkDir(os.path.realpath(config.get('PATHS','SUBS_PATH')))
temp_path = fi.checkDir(os.path.realpath(config.get('PATHS','TEMP_PATH')))
ffmpeg_options = config.get('FFMPEG_OPTIONS','FFMPEG_OPTIONS')
ffmpeg_loglevel = config.get('FFMPEG_OPTIONS','FFMPEG_LOGLEVEL')

class subsBackup:

    def __init__(self, input):
        if isinstance(input,vi.videoInput):
            movie = input
        else:
            movie = vi.videoInput(input)
        backup = os.path.join(subs_path, movie.ofilename + '.mkv')
        self.__backupSubs(movie.input, backup, 'hevc' if movie.uhd else 'h264')
                      
    def __backupSubs(self, inputFile, backupFile, codec):
        cmd = 'ffmpeg -y -loglevel ' + ffmpeg_loglevel + ' ' + ffmpeg_options + ' -vsync 0 -hwaccel cuda -c:v ' + codec + '_cuvid -resize 640x360 -hwaccel_output_format cuda -i ' + inputFile + ' -map 0:v -c:v ' + codec + '_nvenc -b:v 1k -preset p1 -map 0:s -c:s copy "' + backupFile + '"'
        subprocess.call(cmd, stderr=subprocess.STDOUT, shell=True)
               
        
class subsAppend:

    def __init__(self, input, subFile='default'):
        if subFile == 'default':
            self.__findSubs(os.path.basename(input))
        else:
            if os.path.exists(subFile):
                self.subsFile = subFile
        if hasattr(self, 'subsFile'):
            outFile = os.path.join(temp_path, os.path.splitext(os.path.basename(input))[0] + '.mkv')
            self.__append(input, outFile)
            self.__moveFiles(input,outFile)       
        else:
            print('No subs backup found for your input :=',input)
           
        
    def __findSubs(self, inputFile):
        for file in os.listdir(subs_path):
            if file.endswith(".srt"):
                if inputFile.startswith(os.path.splitext(file)[0]):
                    self.subsFile = os.path.join(subs_path,file)
    
    
    def __append(self, inputFile, outFile):
        cmd = 'ffmpeg -y ' + ffmpeg_options + ' -loglevel ' + ffmpeg_loglevel + ' -i "' + inputFile + '" -i "' + self.subsFile + '" -map_metadata 0 -movflags use_metadata_tags -map v:0 -map a:0 -map 1 -c copy -metadata:s:s language=eng "' + outFile + '"'
        subprocess.call(cmd, stderr=subprocess.STDOUT, shell=True)
    
    def __moveFiles(self, inputFile, outFile):
        backupFile = os.path.join(subs_path, os.path.basename(inputFile))
        print('Backing up file')
        shutil.move(inputFile, backupFile)
        print('Replacing file')
        shutil.move(outFile, inputFile)
        print('Done.. Try Now')
        

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:s:",["help","input=","subfile="])
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
        elif opt in ("-s", "--subfile"):
            sub_file = arg
            
    subsAppend(input, sub_file if 'sub_file' in locals() else 'default')

def __usage(exit_code):
    script = os.path.basename(__file__)
    print('Correct Usage:')
    print (script, '-h[--help]  Show this help')
    print (script, '-i[--input] <inputfile> -s[--subfile] (optional)')
    exit(exit_code)    
        
if __name__ == "__main__":
    main()