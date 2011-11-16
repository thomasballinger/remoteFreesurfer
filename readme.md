Spins up amazon ec2 instances and runs freesurfer recon-all on them.

Requires Python (I think anything >= 2.5 should work, but certainly not 3)

Python requirements:

* boto
* fabric

both installable via easy_install

Installation: download the two python files, "fabfile.py" and
"start_instance.py"

In the future this will be simpler, but for now these are the instructions:

Note: You currently need to manually terminate your amazon ec2 instances once 
you're finished with them, or you'll continue to be charged ~$2 per day
for them! Visit this url to do so:
https://console.aws.amazon.com/ec2/

* Get an Amazon EC2 account

* Assign your amazon access key and secret key to the environmental variables AMAZON_ACCESS_KEY and AMAZON_SECRET_KEY respectively

* Start an instance:

type the stuff after a '%'


    % python start_instance.py
    remoteFreesurfer security group already exists
    security rule allowing ssh access already exists
    pending
    pending
    ... (this may take a while)
    running
    Instance now running! Accessible at
    ec2-50-17-82-57.compute-1.amazonaws.com
    using pem
    /home/tomb/tomworkkey.pem
    you need to log on as ec2-user

* You've got your instance up now - if you so choose, manually upload files and run freesurfer, OR

Use the "fab" command line tool to do these things for you:

    % fab -list
    Run freesurfer on local data, and hopefully make troubleshooting possible

    Available commands:

        check        Displays the current status of a subject
        checkScreen  Installs screen if not found at /usr/bin/screen
        checkLicense Prompts for license file text if not yet entered
        download     Download a subject folder to local computer
        remoteFS     Uploads file and runs recon-all on it
        start        Runs recon-all in a screen session
        upload       Uploads a file to home directory

    % fab -H ec2-user@ec2-50-17-174-6.compute-1.amazonaws.com -i ~/tomworkkey.pem remoteFS:brainScan.nii.gz,BillyBob
         
    [ec2-user@ec2-50-17-174-6.compute-1.amazonaws.com] Executing task 'remoteFS'
    [ec2-user@ec2-50-17-174-6.compute-1.amazonaws.com] put: s0001_brain.nii.gz -> /home/ec2-user/s0001_brain.nii.gz
    True
    [localhost] local: ssh -i /home/tomb/tomworkkey.pem ec2-user@ec2-50-17-174-6.compute-1.amazonaws.com screen -m -d recon-all -i s0001_brain.nii.gz -subject test21 -all

    Done.
    Disconnecting from ec2-user@ec2-50-17-174-6.compute-1.amazonaws.com... done.
    
(later)

    % fab -H ec2-user@ec2-50-17-174-6.compute-1.amazonaws.com \
    -i ~/tomworkkey.pem check:BillyBob
    [ec2-user@ec2-50-17-174-6.compute-1.amazonaws.com] Executing task 'check'
    [ec2-user@ec2-50-17-174-6.compute-1.amazonaws.com] run: ls /usr/local/freesurfer/subjects/test15/touch/
    [ec2-user@ec2-50-17-174-6.compute-1.amazonaws.com] out: conform.touch  talairach.touch


    Done.
    Disconnecting from ec2-user@ec2-50-17-174-6.compute-1.amazonaws.com... done.

(much later)

    % fab -H ec2-user@ec2-50-17-174-6.compute-1.amazonaws.com \
        -i ~/tomworkkey.pem download:BillyBob,/home/tomb/fsoutput/

* Finally: REMEMBER TO TERMINATE YOUR INSTANCES!
