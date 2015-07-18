#!/usr/bin/python2
'''
Created on 18th July 2015

@author: Andrew Dean

Motion Notify v0.2 - uploads images and video to Google Drive and sends notification via email.
Detects whether someone is home by checking the local network for an IP address or MAC address and only sends email if nobody is home.
Allows hours to be defined when the system will be active regardless of network presence.

Sends an email to the user at that start of an event and uploads images throughout the event.
At the end of an event the video is uploaded to Google Drive and a link is emailed to the user.
Files are deleted once they are uploaded.

Based on the Google Drive uploader developed by Jeremy Blythe (http://jeremyblythe.blogspot.com) and pypymotion (https://github.com/7AC/pypymotion) by Wayne Dyck 
'''

# This file is part of Motion Notify.
#
# Motion Notify is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Motion Notify is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Motion Notify.  If not, see <http://www.gnu.org/licenses/>.

import smtplib
from datetime import datetime

import os.path
import sys
import subprocess, time

import ConfigParser
import atom.data

import logging.handlers, traceback

from motionnotifygoogledriveupload import MotionNotifyGoogleUpload

logger = logging.getLogger( 'MotionNotify' )
hdlr = logging.handlers.RotatingFileHandler( '/var/tmp/motion-notify.log',
                             maxBytes=1048576,
                             backupCount=3 )
formatter = logging.Formatter( '%(asctime)s %(levelname)s %(message)s' )
hdlr.setFormatter( formatter )
logger.addHandler( hdlr ) 
logger.setLevel( logging.INFO )

def loggerExceptHook( t, v, tb ):
    logger.error( traceback.format_exception( t, v, tb ) )

sys.excepthook = loggerExceptHook

class MotionNotify:
    
    def __init__(self, config_file_path):
        logger.info("Loading config")
        # Load config
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file_path)
        logger.info("Config file read")
        # GMail account credentials
        self.username = self.config.get('gmail', 'user')
        self.password = self.config.get('gmail', 'password')
        self.from_name = self.config.get('gmail', 'name')
        self.sender = self.config.get('gmail', 'sender')

        # Recipient email address (could be same as from_addr)
        self.recipient = self.config.get('gmail', 'recipient')

        # Subject line for email
        self.subject = self.config.get('gmail', 'subject')

        # First line of email message
        self.message = self.config.get('gmail', 'message')

        # Options
        self.delete_files = self.config.getboolean('options', 'delete-files')
        self.send_email = self.config.getboolean('options', 'send-email')

        self.google_drive_folder_link = self.config.get('gmail', 'google_drive_folder_link')
        self.event_started_message = self.config.get('gmail', 'event_started_message')
        
        self.presenceMacs = []
        self.network = None
        
        self.ip_addresses = None
        
        try:
            self.presenceMacs = self.config.get('LAN', 'presence_macs').split(',')
            self.network = self.config.get('LAN', 'network')
        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            pass
        
        try:
            self.ip_addresses = self.config.get('LAN', 'ip_addresses')
        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            pass
        
        try:
            self.forceOnStart = self.config.getint('activate-system', 'force_on_start')
            self.forceOnEnd = self.config.getint('activate-system', 'force_on_end')
        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            pass
        
        logger.info("All config options set")

    def _send_email(self,msg):
        '''Send an email using the GMail account.'''
        senddate=datetime.strftime(datetime.now(), '%Y-%m-%d')
        m="Date: %s\r\nFrom: %s <%s>\r\nTo: %s\r\nSubject: %s\r\nX-Mailer: My-Mail\r\n\r\n" % (senddate, self.from_name, self.sender, self.recipient, self.subject)
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(self.username, self.password)
        server.sendmail(self.sender, self.recipient, m+msg)
        server.quit()

    def _upload(self, media_file_path, eventId, eventTime, fileType):
        '''Upload the media and return the URL'''
        logger.info('Uploading image %s ' % media_file_path)
        if (media_file_path.endswith("jpg")):
            mimeType = "image/" + fileType
        else :
            mimeType = "video/" + fileType
        return MotionNotifyGoogleUpload.upload(media_file_path, eventId + "_" + eventTime + "." + fileType, self.config,
                                               mimeType)
    
    def _system_active(self):
        now = datetime.now()
        system_active = True
        # Ignore presence if force_on specified
        if self.forceOnStart and self.forceOnEnd and \
            now.hour >= self.forceOnStart and now.hour < self.forceOnEnd:
            logger.info( 'System is forced active at the current time - ignoring network presence' )
            return True
        else:
            if self.ip_addresses :
                system_active = self._system_active_ip_based()
            else :
                if self.network and self.presenceMacs:
                    system_active = self._system_active_arp_based()
            logger.info( 'Based on network presence should the email be sent %s', system_active )
        return system_active
    
    def _email_required(self, notify):
        logger.info('Checking if email required')
        if not self.send_email or not notify :
            logger.info( 'Either email is disabled globally or is disabled for this task via command line parameters' )
            return False
        logger.info( 'Email required for this task')
        return True

    def _system_active_arp_based(self):
        if not self.network or not self.presenceMacs:
            return None
        logger.info("Checking for presence via MAC address")
        result = subprocess.Popen( [ 'sudo', 'arp-scan', self.network ], stdout=subprocess.PIPE,stderr=subprocess.STDOUT ).stdout.readlines()
        logger.info("result %s", result)
        for addr in result:
            for i in self.presenceMacs:
                if i.lower() in addr.lower():
                    logger.info( 'ARP entry found - someone is home' )
                    return False
        logger.info( 'No ARP entry found - nobody is home - system is active' )
        return True
    
    def _system_active_ip_based(self):        
        if not self.ip_addresses:
            logger.info("No IP addresses configured - skipping IP check")
            return True
        logger.info("Checking for presence via IP address")
        addresses = self.ip_addresses.split(',')
        for address in addresses :
            #test_string = 'is up'
            test_string = 'bytes from'
            results = subprocess.Popen( ['ping', '-c1', address ], stdout=subprocess.PIPE,stderr=subprocess.STDOUT ).stdout.readlines()
            #results = subprocess.Popen( ['nmap', '-sPn', address ], stdout=subprocess.PIPE,stderr=subprocess.STDOUT ).stdout.readlines()
            logger.info("Nmap result %s", results)
            for result in results:
                if test_string in result :
                    logger.info( 'IP detected - someone is home' )
                    return False
        logger.info( 'IP inactive - nobody is home - system is active' )
        return True

    def upload_media(self, media_file_path, notify, eventId, eventTime, fileType):
        if self._system_active() :
            fileurl = self._upload(media_file_path, eventId, eventTime, fileType)

            if self._email_required(notify):
                msg = self.message + fileurl
                self._send_email(msg)

        if self.delete_files:
            logger.info("Deleting: %s", media_file_path)
            os.remove(media_file_path)

    def send_start_event_email(self, notify) :
        """Send an email showing that the event has started"""
        if self._email_required(notify) and self._system_active() :
            msg = self.event_started_message
            msg += '\n\n' + self.google_drive_folder_link
            self._send_email(msg)


if __name__ == '__main__':
    logger.info("Motion Notify script started")
    try:
        if len(sys.argv) < 3:
            exit(
                'Motion Notify - Usage: uploader.py {config-file-path} {media-file-path} {send-email (1 if email required, if not, 0)} {timestamp} {event_id} {filetype} ')
        cfg_path = sys.argv[1]

        vid_path = sys.argv[2]
        if sys.argv[3] == '1' :
            notify = True
        else :
            notify = False

        if vid_path == 'None':
            MotionNotify(cfg_path).send_start_event_email(notify)
            exit('Start event triggered')

        if len(sys.argv) < 6:
            exit(
                'Motion Notify - Usage: motion-notify.py {config-file-path} {media-file-path} {send-email (1 if email required, if not, 0)} {timestamp} {event_id} {filetype} ')

        eventTime = sys.argv[4]
        eventId = sys.argv[5]
        fileType = sys.argv[6]
        if not os.path.exists(cfg_path):
            exit('Config file does not exist [%s]' % cfg_path)

        if not os.path.exists(vid_path):
            exit('Video or image file does not exist [%s]' % vid_path)

        MotionNotify(cfg_path).upload_media(vid_path, notify, eventId, eventTime, fileType)
    except Exception as e:
        exit('Error: [%s]' % e)
