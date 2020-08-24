import os, subprocess
	
def getFileList(inDirectory, extensions=[''], fileList=[]):
    for entry in os.listdir(inDirectory):
        if os.path.isdir(inDirectory+"/"+entry):
            getFileList(inDirectory+"/"+entry,extensions, fileList)
        if entry.endswith(tuple(extensions)):
            fileList.append(inDirectory+"/"+entry) 
    return fileList

def getLargestFileFromList(listOfFiles):
	return sorted((os.path.getsize(s), s) for s in listOfFiles)[-1][1] if listOfFiles else ''

def getLargestFileFromDir(dir, extensions=['']):
	print(dir, extensions)
	return getLargestFileFromList(getFileList(dir, extensions))
	
def checkDir(dirtocheck):
	dir = os.path.abspath(dirtocheck)
	if os.path.exists(dir):
		if not os.path.isdir(dir):
			print ('There is an issue oiwth ther pathe specified, as its not a directory:')
			print (dir)
			exit(2)
	else:
		# If it doesnt exist but is a dir its likely a junction....
		if os.path.isdir(dir):
			try:
				output = subprocess.check_output('fsutil reparsepoint query ' + dir)
				output = output.decode("utf-8")
				for line in output.split('\n'):
					if line.split(':', 1)[0] == 'Print Name': dir = line.split(':', 1)[1].strip()
				
			except:
				pass
		if not os.path.exists(dir): os.makedirs(dir)
	return os.path.abspath(dirtocheck) + os.sep