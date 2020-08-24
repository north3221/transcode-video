# transcode-video

## prerequisites
### ffmpeg 
	build with following options as a minimum (there will be more) and on your PATH:	
*	--enable-libbluray
*	--enable-libx264 
*	--enable-libx265

### mediainfo
	(also on PATH)


### config.ini
	This holds the settings

### create-video-outputs.py
	This is the python script that transcodes the video

#### usage:
	create-video-outputs.py -i[--input] <inputfile> -s[--sample] (optional)
	NB sample time is a setting in config.ini


#### Window drag and drop:
There are two dragand drop (dnd) files. These are so you can drag and drop your video file or bluray folder for full transcode or sample:
*	dnd-video-transcode.bat
*	dnd-video-transcode-sample.bat




