import ctypes, sys, subprocess, configparser, os, time

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if is_admin():
    print('Checking for disk info')
    config = configparser.ConfigParser()
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.realpath(os.path.join(base_path,'config/config.ini'))
    config.read(config_path)
    backup_path = config.get('PATHS','BACKUP_PATH')
    log_path = os.path.realpath(os.path.join(base_path,config.get('PATHS','LOG_PATH')))
    call_transcode = 'true' == config.get('DECRYPT_BLURAY','CALL_TRANSCODE')
    cmd = 'makemkvcon64 -r info'
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except Exception as e:
        output = e.output.decode('utf-8')
    for line in output.split('\n'):
        if line.startswith('DRV') and not line.split(',')[4] == '""':
            disk = line.split(',')[0].split(':')[1]
            title = line.split(',')[5].strip('"')
            drive = line.split(',')[6]
    if len(title) > 1:
        # TODO likely going to cause an issue if any spaces in path or title
        backup = '"' + os.path.realpath(os.path.join(base_path,backup_path, title)) + '"'
        log = os.path.join(log_path, 'makemkv-' + title +'.log')
        bcmd = 'makemkvcon64 backup --decrypt --cache=256 -r --progress=-same disc:' + disk + ' ' + backup
        print('Running Bluray decrypt, check log for details:=', log)
        print('Running backup of', title, 'to', backup)
        with open(log, 'w+') as log_file:
            subprocess.call(bcmd, stderr=subprocess.STDOUT, stdout=log_file)        
            # Check for errors
            log_output = log_file.read()
        errors = log_output.upper().count("ERROR")
        if errors > 0:
            print('Errors occured in decrypt job, see log for details')
        else:        
            print('Finished backup')
            if call_transcode:
                print ('Calling transcode')
                transcode = 'python ' + os.path.realpath(os.path.join(base_path, 'transcode-video.py')) + ' -i ' + backup
                os.system(transcode)
                
    else:
        print ('No disc found, is admin set properly, is there a disk, does the drive need opening and closing (sometimes helps)')
        print ('exiting in 10')
        time.sleep(10)
else:
    # Re-run the program with admin rights
    print('Requesting Admin')
    run = os.path.realpath(__file__)
    code = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, run, None, 1)
