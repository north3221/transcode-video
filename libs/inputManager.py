from enum import Enum

class inputType(Enum):
	blurayBackup = 1
	videoFile	=	2
	

def getFfmpegInput (inputType, inputPath):
	inputPath = checkDir(inputPath)
	inputswitch = {
		inputType.blurayBackup:		'bluray:' + inputPath,
		inputType.videoFile:		inputPath
	}

	return inputswitch.get(inputType, "Invalid Input")
	
def checkDir(inputCheck):
	if ' ' in inputCheck and not inputCheck.startswith('"'):
		inputCheck = '"' + inputCheck + '"'
	return inputCheck
