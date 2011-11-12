#!/usr/bin/env python
"""Run freesurfer on local data, and hopefully make troubleshooting possible"""

from fabric.api import run, sudo, local
from fabric.operations import put, get
from fabric.contrib.files import exists
from fabric.api import env

subjects_dir = '/usr/local/freesurfer/subjects/'

def upload(f):
    """Uploads a file to home directory"""
    put(f, '')

def checkScreen():
    """Installs screen if not found at /usr/bin/screen"""
    match = exists('/usr/bin/screen')
    print match
    if not match:
        sudo('yum -y install screen')

def start(f, subject=None):
    """Runs recon-all in a screen session"""
    checkScreen()
    if not subject:
        subject = f.split('/')[-1].split('.')[0]
    if exists(subjects_dir + subject):
        raise EnvironmentError('Freesurfer subject directory already exists! Use a new subject name or delete the subject folder')
    fs_cmd = 'recon-all -i %s -subject %s -all' % (f, subject)

    # these two options don't work
    #run("nohup "+fs_cmd+" >& fs.log < /dev/null") 
    #run("screen -m -d "+fs_cmd)

    # hack replacing those options
    local('ssh -i '+env.key_filename[0]+' '+env.host_string+' screen -m -d '+fs_cmd)

def remoteFS(f, subject=None):
    """Uploads file and runs recon-all on it"""
    upload(f)
    start(f, subject)

def check(subject):
    touches =  run('ls ' + subjects_dir + subject + '/touch/')
    finished = exists(subjects_dir + subject + '/touch/wmaparc.stats.touch')
    if finished:
        return True
    else:
        return False

def download(subject, dest):
    if not dest:
        dest = ''
    get(subjects_dir + subject, dest)
