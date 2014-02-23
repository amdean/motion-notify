motion-notify
=============

Motion Notify is a notification system for Linux Motion providing upload to Google Drive and email notificaiton when you're not home.
This carries out the following:

-Sends an email when motion detection event starts
-Uploads images to Google Drive whilst an event is occuring
-Uploads a video to Google Drive when the event ends
-Sends an email when the event ends with a link to the video
-Detects whether you're at home by looking for certain IP addresses on your local network and doesn't send alerts if you're home
-Allows you to specify hours when you want to receive alerts even if you're at home

Only receive alerts when you're not home
The script detects whether you're at home by checking the network for the presence of certain devices by IP address or MAC address.
It's highly recommended to use IP rather than MAC. If you choose to use MAC you will need to run the script (and Motion) as root as it uses ARP - this isn't recommended. IP detection uses ping so will run as a regular user.
Specify either a comma separated list of IP addresses or a comma separated list of MAC addresses. IP addresses take priority so if you specify those, the MAC addresses will be ignored.
Note that mobile phones often don't retain a constant connection to the wireless network even though they show that they are connected. They tend to sleep and then just reconnect occassionally to reduce battery life.
This means that you might get a lot of false alarms if you just use a mobile phone IP address.
Adding lots of devices that are only active when you're at home will reduce false alarms - try things like your Smart TV, desktop PC etc as well as any mobile phones.
A later release will include improvements to not just check if a device is present but also to check if a device has been present in the last X number of minutes.
It's highly recommended to configure your devices to use static IP's to prevent the IP addresses from changing.

Google Drive setup
Login to Google Drive and create a folder where images and video will be upload to (the supplied config file uses "CCTV" as folder the name but you can change that if needed)
Hint - if you're concerned about storing your password for your Google account in the clear in the config text file there is a solution. Create another Google account just for sending alerts.
Create the folder in the Google Drive for the new account you created and then share that folder with your main Google account. That way you don't have to use the password for your main account.

Installation
There's no automated installation yet so this is the current process

Create a directory:
sudo mkdir /etc/motion-notify

Copy motion-notify.cfg, motion-notify.py and create-motion-conf-entries.txt to the directory you created

Create the log file and set the permissions
sudo touch /var/tmp/motion-notify.log
sudo chown motion.motion /var/tmp/motion-notify.log
sudo chmod 664 /var/tmp/motion-notify.log


Edit the config file and enter the following:
-Google account details into the GMail section of the config file
-Email address to send alerts to
-The URL of the folder you created in your Google account (just copy and paste it from the browser). This will be sent in the alert emails so that you can click through to the folder
-The name of the folder you created eg. CCTV
-The hours that you always want to recieve email alerts even when you're home
-Either enter IP addresses or MAC addresses (avoid using MAC addresses) which will be active when you're at home

Change the permissions
sudo chown motion.motion /etc/motion-notify/motion-notify.py
sudo chown motion.motion /etc/motion-notify/motion-notify.cfg
sudo chmod 744 motion.motion /etc/motion-notify/motion-notify.py
sudo chmod 600 motion.motion /etc/motion-notify/motion-notify.cfg

Create the entry in the Motion conf file to trigger the motion-notify script when there is an alert
sudo cat /etc/motion-notify/create-motion-conf-entries.txt >> /etc/motion/motion.conf
rm /etc/motion-notify/create-motion-conf-entries.txt


Motion will now send alerts to you when you're devices aren't present on the network