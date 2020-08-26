import ctypes, sys, subprocess, configparser, os


def is_admin():
	try:
		return ctypes.windll.shell32.IsUserAnAdmin()
	except:
		return False

if is_admin():
	config = configparser.ConfigParser()
	config.read('config.ini')
	backup_path = config.get('PATHS','BACKUP_PATH')
	log_path = config.get('PATHS','LOG_PATH')
	call_transcode = 'true' == config.get('DECRYPT_BLURAY','CALL_TRANSCODE')
	cmd = 'makemkvcon -r info'
	try:
		output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
	except Exception as e:
		output = e.output.decode('utf-8')
	for line in output.split('\n'):
		if line.startswith('DRV') and not line.split(',')[4] == '""':
			disk = line.split(',')[0].split(':')[1]
			title = line.split(',')[5].strip('"')
			drive = line.split(',')[6]
	
	# TODO likely going to cause an issue if any spaces in path or title
	backup = os.path.join(backup_path, title)
	log = os.path.join(log_path, 'makemkv-' + title +'.log')
	bcmd = 'makemkvcon backup --decrypt --cache=256 -r --progress=-same disc:' + disk + ' ' + backup
	print('Running backup of', title, 'to', backup)
	with open(log, 'w') as log_file:
		subprocess.call(bcmd, stderr=subprocess.STDOUT, stdout=log_file)
		
	transcode = 'python ' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'create-video-outputs.py -i ' + os.path.abspath(backup))
	if call_transcode: os.system(transcode)

else:
	# Re-run the program with admin rights
	print('Requesting Admin')
	run = os.path.realpath(__file__)
	code = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, run, None, 1)