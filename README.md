skydriveannex
=========

Hook program for gitannex to use skydrive as backend

# Requirements:

    python2
    python-yaml

Credit for the Skydrive api interface goes to https://github.com/mk-fg/python-skydrive

# Install
Clone the git repository in your home folder.

    git clone git://github.com/TobiasTheViking/skydriveannex.git 

This should make a ~/skydriveannex folder

# Setup
Run the program once to set it up.

    cd ~/skydriveannex; python2 skydriveannex.py

# Commands for gitannex:

    git config annex.skydrive-hook '/usr/bin/python2 ~/skydriveannex/skydriveannex.py'
    git annex initremote skydrive type=hook hooktype=skydrive encryption=shared
    git annex describe skydrive "the skydrive library"
    git annex content imap exclude=largerthan=100mb
