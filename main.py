import ftplib
import configparser as cfg
import logging as lg
import os
import hashlib as hl
import json

def hash1(hfile):
    return hl.sha1(open(hfile, "rb").read()).hexdigest()

def hash256(hfile):
    return hl.sha256(open(hfile, "rb").read()).hexdigest()

config = cfg.ConfigParser()
config.read('config.ini')

# Open the Launcher Config File (specified in config.ini) and parse it with json
with open(config['Files']['LauncherConfig'], "r") as f:
    launcherconfig = json.load(f)

open(config['Files']['Log'], 'a').close()
log_level = config['Settings']['Loglevel'].upper()
lg.basicConfig(filename=config['Files']['Log'], level=log_level,
               format='%(asctime)s : %(message)s', datefmt='%I:%M:%S')

lg.info('Connecting to FTP server and downloading files') 
ftp = ftplib.FTP()
ftp.connect(config['FTP']['Host'], config['FTP']['Port'])
ftp.login(config['FTP']['User'], config['FTP']['Password'])
# Go to the directory where the files are (specified in config.ini) and download them
ftp.cwd(config['FTP']['ModFileDir'])
# Check if temp dir exists, if not create it
main_file_path = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(main_file_path + "/temp"):
    os.makedirs(main_file_path + "/temp")
if not os.path.exists(main_file_path + "/temp/mods"):
    os.makedirs(main_file_path + "/temp/mods")
if not os.path.exists(main_file_path + "/temp/rps"):
    os.makedirs(main_file_path + "/temp/rps")
for modfile in ftp.nlst():
    lg.debug("Downloading file: " + modfile)
    with open(main_file_path + "/temp/mods/" + modfile, 'wb') as f:
        ftp.retrbinary('RETR ' + modfile, f.write)
ftp.cwd(config['FTP']['RPFileDir'])
for rpfile in ftp.nlst():
    lg.debug("Downloading file: " + rpfile)
    with open(main_file_path + "/temp/rps/" + rpfile, 'wb') as f:
        ftp.retrbinary('RETR ' + rpfile, f.write)
ftp.quit()
lg.info('Finished downloading files')

# Go trough the files and put their name, hashes and size in a dict and put the dicts in a list
lg.info('Calculating hashes and sizes of files')
modfiles = []
for modfile in os.listdir(main_file_path + "/temp/mods"):
    modfiles.append({'name': modfile, 'hash1': hash1(main_file_path + "/temp/mods/" + modfile),
                     'hash256': hash256(main_file_path + "/temp/mods/" + modfile),
                     'size': os.path.getsize(main_file_path + "/temp/mods/" + modfile),
                     'url': config['Web']['BaseURL'] + modfile})
launcherconfig['additional']['mods'] = modfiles
rpfiles = []
for rpfile in os.listdir(main_file_path + "/temp/rps"):
    rpfiles.append({'name': rpfile, 'hash1': hash1(main_file_path + "/temp/rps/" + rpfile),
                    'hash256': hash256(main_file_path + "/temp/rps/" + rpfile),
                    'size': os.path.getsize(main_file_path + "/temp/rps/" + rpfile),
                    'url': config['Web']['BaseURL'] + rpfile})
launcherconfig['additional']['config/immersiverailroading'] = rpfiles
lg.info('Finished calculating hashes and sizes of files')
with open(config['Files']['LauncherConfig'], "w") as f:
    json.dump(launcherconfig, f, indent=4)
lg.info('Finished writing the launcher config file')