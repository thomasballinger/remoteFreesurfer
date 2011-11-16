#!/usr/bin/env python
"""Run freesurfer on local data, and hopefully make troubleshooting possible"""

from fabric.api import run, sudo, local
from fabric.operations import put, get, prompt
from fabric.contrib.files import exists, append
from fabric.api import env
import os

subjects_dir = '/usr/local/freesurfer/subjects/'
license_location = '/usr/local/freesurfer/.license'

def upload(f):
    """upload:/local/file
    Uploads a file to home directory"""
    put(f, '')

def checkScreen():
    """checkScreen
    Installs screen if not found at /usr/bin/screen"""
    match = exists('/usr/bin/screen')
    print match
    if not match:
        sudo('yum -y install screen')

def checkLicense():
    """checkLicense
    Checks for license, prompts for license text if not found"""
    if exists(license_location):
        return True
    else:
        print 'Freesurfer .license file not found!'
        print 'If you don\'t already have one, check out'
        print 'http://surfer.nmr.mgh.harvard.edu/fswiki/Registration'
        line1 = prompt('enter first line (of 3) of freesurfer .license file',
                validate='.*[@].*')
        line2 = prompt('enter second line of freesurfer .license file',
                validate='\d+')
        line3 = prompt('enter first line of freesurfer .license file',
                validate='.*')
        append(license_location, '\n'.join([line1, line2, line3]))

def uploadLicense(filename):
    """uploadLicense:/local/file/.license
    Uploads a string or string found in file to .license file"""
    upload(filename, license_location)

def start(f, subject=None):
    """start:remoteFile[,subjectName]
    Runs recon-all in a screen session"""
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
    """remoteFS:/local/file[,subjectName]
    Uploads file and runs recon-all on it"""
    upload(f)
    start('/home/ec2-user/'+os.path.basename(f), subject)

def check(subject):
    """check:subjectName
    Displays the touches folder of a Freesurfer subject"""
    touches =  run('ls ' + subjects_dir + subject + '/touch/')
    finished = exists(subjects_dir + subject + '/touch/wmaparc.stats.touch')
    if finished:
        return True
    else:
        return False

def download(subject, dest):
    """download:subjectName,local/file/or/folder
    Downloads a subject folder"""
    if not dest:
        dest = ''
    get(subjects_dir + subject, dest)
