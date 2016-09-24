#!/usr/bin/env bash

# Installs motion-notify and all required dependencies.
# Pre-requisites: Run script as root, ensure a motion.motion user exists, ensure that /etc/motion-notify does NOT exist
# Refer to the README for additional steps required for configuring Google Drive, email and etc (those steps aren't covered by this script)
# If you're upgrading motion-notify, move your existing motion-notify folder to a new location first and then copy your creds.p12 file across after running the install script and then update your new config file

# Update APT and install dependencies
apt-get update
apt-get install python-pip
pip install --upgrade PyDrive
pip install --upgrade enum34
pip install --upgrade oauth2client
pip install --upgrade google-api-python-client
apt-get install python-openssl

# Install git and clone motion-notify into the destination directory
apt-get install git
git clone https://github.com/amdean/motion-notify.git /etc/motion-notify
chown -R motion.motion /etc/motion-notify
chmod +x /etc/motion-notify/motion-notify.py

# Create the log files and lock files and set ownership and permissions
touch /var/tmp/motion-notify.log
chown motion.motion /var/tmp/motion-notify.log
chmod 664 /var/tmp/motion-notify.log
touch /var/tmp/motion-notify.lock.pid
chmod 664 /var/tmp/motion-notify.lock.pid
chown motion.motion /var/tmp/motion-notify.lock.pid