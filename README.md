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


Installation

Install Python Libraries
sudo apt-get update
sudo apt-get install python-pip
sudo pip install PyDrive
sudo pip install enum34
sudo apt-get install python-openssl

Create a directory:
sudo mkdir /etc/motion-notify

Copy motion-notify.cfg, motion-notify.py and create-motion-conf-entries.txt to the directory you created

Create the log file and set the permissions
sudo touch /var/tmp/motion-notify.log
sudo chown motion.motion /var/tmp/motion-notify.log
sudo chmod 664 /var/tmp/motion-notify.log


Configurations

Google Drive Config
Google drive authentication is done using a service account via key authentication. The service account is given access only to the folder you specify in Google Drive.

Login to Google Drive and create a folder where images and video will be upload to
Enter the ID of the folder into the "folder" field in the config file (if the URL of the folder is https://drive.google.com/drive/folders/0Bzt4FJyYHjdYhnA3cECdTFW3RWM then the ID is 0Bzt4FJyYHjdYhnA3cECdTFW3RWM.
Next you need to get some account credentials from the Google Developers console - this will allow motion-notify to upload files to Google Drive.
Go to https://console.developers.google.com/
From the "Select a project" dropdown at the top of the page choose "Create a project"
Enter "motion-notify" as the project name (or anything else that you want to call it)
Once the project is created you'll be take to the project dashboard for that project.
Go to APIs & auth > APIs > Drive API and click "Enable API"
Go to APIs & auth > Credentials and choose "Create new Client ID" and select "Service Account" as the application type.
You'll receive a download containing a JSON file.
Generate a new P12 key for the service account you just created using the button underneath the details of the service account. Save this file in the /etc/motion-notify directory and rename it to cred.p12.
The service account has an email address associated with it which will @developer.gserviceaccount.com. Copy that email address and enter it into the "service_user_email" field in the config file.
You now need to allow the service account access to your Google Drive folder.
    Go to the Google Drive folder where you want images and videos to be uploaded
    Click on the share icon
    Enter the email address of your service account and ensure that "Can edit" is selected.


Email config
Enter the following configuration for emails:
-Google account details into the GMail section of the config file (this is just to send emails so you could setup another Google account just for sending if you're worried about storing your account password in the clear).
-Email address to send alerts to
-The URL of the folder you created in your Google account (just copy and paste it from the browser). This will be sent in the alert emails so that you can click through to the folder

Notification Config
-The hours that you always want to receive email alerts even when you're home
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
