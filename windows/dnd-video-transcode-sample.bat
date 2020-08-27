@echo off
TITLE Transcode video Job
COLOR 3f
%~d0
cd %~dp0..
python transcode-video.py -i %1 -s true
pause