#!/usr/bin/env python
"""Run freesurfer on local data, and hopefully make troubleshooting possible"""

import fabric
from fabric.api import run, sudo
from fabric.operations import put, get
from fabric.contrib.files import exists

subject_dir = '/usr/local/freesurfer/subjects/'

def upload(f):
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
    if exists(subject_dir + subject):
        raise EnvironmentError('Freesurfer subject directory already exists! Use a new subject name or delete the subject folder')
    fs_cmd = 'recon-all -i %s -subject %s -all' % (f, subject)

    #run(fs_cmd)

    # couldn't get this working, maybe it just doesn't work with fabric
    #run("nohup '"+fs_cmd+" >& fs_output.log < /dev/null' &")

    cmd = "screen -m -d bash -c \""+fs_cmd+"; read x\""
    print cmd
    run(cmd)

def test():
    run("screen -list")


def remoteFS(f, subject=None):
    """Uploads file and runs recon-all on it"""
    upload(f)
    start(f, subject)

def check(subject):
    touches =  run('ls ' + subjects_dir + subject + '/touch/')
    finished = exists(subjects_dir + subject + '/touch/wmaparc.stats.touch')
    if output:
        return True
    else:
        return False

def download(subject, dest):
    if not dest:
        dest = ''
    get(subject_dir + subject, dest)
