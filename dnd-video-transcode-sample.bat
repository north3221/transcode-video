@echo off
TITLE Transcode video Job
COLOR 3f
%~d0
cd %~dp0
python create-video-outputs.py -i %1 -s true
pause