#!/usr/bin/env python
"""Script for running Freesurfer on an amazon EC2 instance

Requires amazon access key and amazon secret key - currently script
looks for these in the environment.

Warning: if you already have a security group called "remoteFreesurfer",
this script will enable access to port 22 tcp!  This isn't dangerous on
the machines we boot up, since only keypair access is allowed via ssh,
but could be very dangerous if you have other instances in this security group.
"""
import os
import sys
import time
from glob import glob

import boto.ec2

def get_security_group(conn):
    FS_sec_name = 'remoteFreesurfer'
    security_groups = conn.get_all_security_groups()
    #print security_groups
    try:
        fs_security_group = [sg for sg in security_groups if sg.name == FS_sec_name][0]
        print FS_sec_name, 'security group already exists'
    except IndexError:
        fs_security_group = conn.create_security_group(FS_sec_name, 'Freesurfer Security Group')
        print 'new security group created'
    try:
        fs_security_group.authorize(ip_protocol='tcp', from_port=22, to_port=22, cidr_ip='0.0.0.0/0')
        #allowing any ip access in case your ip changes
        print 'new security rule created, allowing ssh access'
    except boto.ec2.connection.EC2ResponseError:
        print 'security rule allowing ssh access already exists'
    return fs_security_group

#create a new key pair
def get_key_pair_name_and_pem_file(conn, pem_filename=None):
    """Tries to find existing key pairs, otherwise creates new"""
    #TODO if existing key found, should check it somehow if possible
    #       (right now only checked to see if it exists)

    def new_key():
        new_key_pair_name, counter = 'FSkey', 0
        while new_key_pair_name in [k.name for k in keys]:
            counter += 1
            new_key_pair_name = 'FSkey'+str(counter)
        key = conn.create_key_pair(new_key_pair_name)
        print 'new key pair created:', new_key_pair_name
        key.save('.')
        print 'new key pair pem saved to current directory', os.path.abspath('.')
        return new_key_pair_name, os.path.join(os.path.abspath(), name+'.pem')

    keys = conn.get_all_key_pairs()
    if pem_filename:
        if not os.path.exists(pem_filename):
            raise EnvironmentError("pem file does not exist")
        pems = [pem_file]
    else:
        pems = glob(os.path.expanduser('~/*.pem'))
        pems.extend(glob('./*.pem'))
    #print pems
    for pem in pems:
        name = os.path.basename(pem)[:-4]
        match = [k for k in keys if k.name == name]
        if match:
            return name, os.path.abspath(pem)
    else:
        return new_key()

def get_ec2_connection():
    """Returns connection object"""
    access_key = os.environ['AMAZON_ACCESS_KEY']
    secret_key = os.environ['AMAZON_SECRET_KEY']
    conn = boto.ec2.connection.EC2Connection(access_key, secret_key)
    return conn

def get_ami(conn):
    # This one isn't good anymore, was made private because it
    #  included a licence file
    # ami_id for 060244368407/FREESURFER51
    #fs51_ami_id = 'ami-5dc10834'

    # ami_id for Basic 32-bit Amazon Linux AMI 2011.09
    #ami_id = 'ami-31814f58'

    # ami_id for something that was on the freesurfer wiki
    ami_id = 'ami-5dc10834'
    ami = conn.get_image(ami_id)
    return ami

def start_instance():
    """Returns how to access started instance. Blocks until instance is ready."""
    conn = get_ec2_connection()
    key, pem = get_key_pair_name_and_pem_file(conn)
    secgrp = get_security_group(conn)
    image = get_ami(conn)

    reservation = image.run(key_name=key,
            security_groups=[secgrp],
            instance_type='m1.small')

    instance = reservation.instances[0]
    instance.add_tag('remoteFreesurfer')
    while True:
        time.sleep(10)
        print instance.update()
        if instance.state == 'running':
            return instance.public_dns_name, pem

if __name__ == '__main__':
    conn = get_ec2_connection()
    host, pem = start_instance()
    print 'Instance now running! Accessible at'
    print host
    print 'using pem'
    print pem
    print 'you need to log on as ec2-user'
