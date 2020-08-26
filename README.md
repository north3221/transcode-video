# transcode-video

## prerequisites
### ffmpeg 
build with following options as a minimum (there will be more) and on your PATH:	
*	--enable-libbluray
*	--enable-libx264 
*	--enable-libx265

### MakeMKV
This is used for decrypting the blurray so only needed for the decrypt job
NB if decrypting yourself or using already decrypted output, is not needed
Required to be on your PATH

### mediainfo
(also on PATH)

### config.ini
This holds the settings

### create-video-outputs.py
This is the python script that transcodes the video

#### usage:
	create-video-outputs.py -i[--input] <inputfile> -s[--sample] (optional)
	NB sample time is a setting in config.ini
	
### decrypt-bluray.py
This is the python script that uses MakeMKV to decrypt a bluray in a drive
Has an option in config.ini ('CALL_TRANSCODE') which auto calls the transcode job once dycrypted if set to true

#### Window drag and drop:
There are two dragand drop (dnd) files. These are so you can drag and drop your video file or bluray folder for full transcode or sample:
*	dnd-video-transcode.bat
*	dnd-video-transcode-sample.bat
There is also a bat for running decrypt by double clicking
*	dnd-video-transcode-sample.bat





