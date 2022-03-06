@echo off
TITLE IMPORTING SUBS
COLOR 71
%~d0
cd %~dp0..

set /p input_sub_file="Enter Sub File (srt) path: Press Enter for default := "
if not "%input_sub_file%"=="" set sub_file=%input_sub_file%

set args=-i %1
echo %1
if not "%sub_file%"=="" set args=%args% -s %sub_file%
echo %args%

python libs\subs.py %args%
pause
