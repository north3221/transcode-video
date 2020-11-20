import subprocess

class AtmosInfo:

    def __init__(self, mediainfo_input):
        print('Checking for Dolby Atmos audio....')
        self.__setAtmos(mediainfo_input)
            
    def __setAtmos(self, mi):
        delim = '/'
        cmdMediaIffo = 'mediainfo --Inform="Audio;%Format_Commercial_IfAny%' + delim + '" "' + mi + '"'
        try:
            output = subprocess.check_output(cmdMediaIffo, stderr=subprocess.STDOUT)
        except Exception as e:          
            outpute = e.output
            print (outpute)
            exit()
        output = output.decode("utf-8")
        self.exists = 'Atmos' in output
        if self.exists: 
            print('Atmos found, setting stream info.....')
            self.stream = [i for i, s in enumerate(output.split('/')) if 'Atmos' in s][0]
