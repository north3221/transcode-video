# transcode-video

Transcoding video and compressing, using ffmpeg. Will take an input of a video file or a bluray folder.
There are a bunch of settings you can use in the config.ini to adjust to your liking, like crf and maxrate.

It will analyse the video and see if its UHD or HD. If UHD it will output both a UHD and HD copy.

There is also a decrypt that will take a bluray from optical drive and decrypt it to your chosen location (set in config)
This comes with the option to pass the backed-up bluray directly to the transcode script.

You can also choose to bypass the user check of movie info (user check alows you to overwrite title, year etc), so it can just do the lot in one go.
If doing that I suggest using the MovieDB option and setting a api-key so it tries to get the right title and year.
Then also set the 'USER_CHECK_CONFIDENCE' so that it will still check with you if it cant find a great match

If it doesnt match ans askes you, now you can input a new search for moviedb, it will return a list of all found on moviedb and let you selct the correct title

There is an option to backup subs. At the moment I cant get subs burnt on as part of the complex filtering. So it creates a backup file, with really
low resolution to keep file size small. There is then a function to add subs, but right now needs an external program and manual intervention. You need
to create the subs file using something like subedit, to convert the image subs to text, then this imports them to your video

There are win bat files in the windows folder, so if you set movie db, and no user check you can put a bluray in and just double click:	`run-bluray-decrypt.bat`


### prerequisites
#### ffmpeg 
build with following options as a minimum (there will be more) and on your PATH:	
*	--enable-libbluray
*	--enable-libx264 
*	--enable-libx265

For updating ffmpeg, I use media-autobuild_suite:		https://github.com/m-ab-s/media-autobuild_suite/wiki

#### MakeMKV
This is used for decrypting the blurray so only needed for the decrypt job
NB if decrypting yourself or using already decrypted output, is not needed
Required to be on your PATH

Download from 				http://www.makemkv.com/download/
Beta license to try 		https://www.makemkv.com/forum/viewtopic.php?t=1053

#### mediainfo
(also on PATH)

#### The Movie DB (optional)
If you are using this option you need to add your api-key inside 'config/secret/api-key'

### config.ini
This holds the settings

### create-video-outputs.py
This is the python script that transcodes the video

#### usage:
	create-video-outputs.py -i[--input] <inputfile> -s[--sample] (optional)
	NB sample time is a setting in config.ini
	
### decrypt-bluray.py
This is the python script that uses MakeMKV to decrypt a bluray in a drive
Has an option in config.ini `CALL_TRANSCODE` which auto calls the transcode job once dycrypted if set to true

### The Movie Database
There is an option in the config.ini `CALL_MOVIEDB` to make a call to The Movie Database to get the movie info
It gets info and overwrites title and year on the info. Don't forget the pre-requisite to set api-key

#### Window folder (with drag and drop):
There are three drag and drop (dnd) files.

These two are so you can drag and drop your video file or bluray folder for full transcode or sample:
*	`dnd-video-transcode.bat`	
*	`dnd-video-transcode-sample.bat`
This one is for addind a subs file (.srt) to your movie. So if you used backup subs option, there will be a file in your subs backup folder with all the sub streams.
You need to convert the one you want to a text .set file and drag your video on here, it will ask you for .srt file loacation, or just leave it is sub backup folder and will pick up by default
NB I use subtitle edit: https://github.com/SubtitleEdit/subtitleedit/releases
*	`dnd-import-subs.bat`
There is also a bat for running decrypt by double clicking
So if set the call transcode to true, calling Movie DB and set check user to false can double click and it will run the lot
*	`run-bluray-decrypt.bat`









