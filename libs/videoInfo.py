import subprocess, io

class videoInfo:

    def __init__(self, input):
        print('Analyzing video......')
        self.vstream = 'v:0'
        self.astream = 'a:0'
        self.__initInfo(input)
        self.__chapters()

    def __initInfo(self, input):
        ffprobe_cmd = 'ffprobe -v quiet -prefix -unit -show_streams -select_streams v:0 -show_frames -read_intervals "%+#1" -of default=noprint_wrappers=1 -i  ' + input
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
                exec("self." + p[0].replace(' ', '_') + " = '" + p[1].replace('\r','') + "'")
        # set duration
        ffprobe_cmd = 'ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 ' + input
        try:
            self.duration = subprocess.check_output(ffprobe_cmd, stderr=subprocess.STDOUT)
            self.duration = float(self.duration.decode("utf-8").split('\n')[0])     
        except:
            print('Issue getting duration - will likely crash')
        
        # set crop
        crop_cmd = 'ffmpeg -stats -hide_banner -loglevel info -ss 500 -i ' + input + ' -vframes 100 -vf cropdetect -f null -'
        try:
            output = subprocess.check_output(crop_cmd, stderr=subprocess.STDOUT)
            output = output.decode().split('\n')
            crop_params = [None, None, None, None]            
            for line in output:
                if 'Parsed_cropdetect' in line:
                    params=line.split('=')[-1].split(':')
                    for i in range(4):
                        if i < 2:
                            crop_params[i] = params[i] if crop_params[i] is None or int(params[i]) > int(crop_params[i]) else crop_params[i]
                        else:
                            crop_params[i] = params[i] if crop_params[i] is None or int(params[i]) < int(crop_params[i]) else crop_params[i]
            self.crop_params = ':'.join(crop_params).rstrip('\r')
        except:
            print("Getting Crop failed")        
            
    
    def __chapters(self):
        chapter_size = 300
        start = 0
        cid = 1
        chapters = [';FFMETADATA1']
        while start < self.duration:
            chapters.append('[CHAPTER]')
            chapters.append('TIMEBASE=' + self.time_base)
            chapters.append('START=' + str(start * int(self.time_base.split('/')[1])))
            end = start + chapter_size
            if end > self.duration: end = self.duration
            chapters.append('END=' + str(end  * int(self.time_base.split('/')[1])))
            chapters.append('title=Chapter ' + str(cid))
            start = end
            cid = cid + 1
        self.chapters = io.StringIO('\n'.join(chapters))
        
    # Adding in a safer get() method. Can call attributes directly but will error if doesnt exist, so this is a safe way to get attribute
    def get(self, index):
        return getattr(self, index, None)