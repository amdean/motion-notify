#!/usr/bin/python2
'''
Created on 29 December 2013

@author: Andrew Dean

Motion Notify - uploads images and video to Google Drive and sends notification via email.
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

import gdata.data
import gdata.docs.data
import gdata.docs.client
import ConfigParser
import atom.data

import logging.handlers, traceback

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
        config = ConfigParser.ConfigParser()
        config.read(config_file_path)
        logger.info("Config file read")
        # GMail account credentials
        self.username = config.get('gmail', 'user')
        self.password = config.get('gmail', 'password')
        self.from_name = config.get('gmail', 'name')
        self.sender = config.get('gmail', 'sender')

        # Recipient email address (could be same as from_addr)
        self.recipient = config.get('gmail', 'recipient')

        # Subject line for email
        self.subject = config.get('gmail', 'subject')

        # First line of email message
        self.message = config.get('gmail', 'message')

        # Folder (or collection) in Docs where you want the media to go
        self.folder = config.get('docs', 'folder')

        # Options
        self.delete_files = config.getboolean('options', 'delete-files')
        self.send_email = config.getboolean('options', 'send-email')

        self._create_gdata_client()

        self.google_drive_folder_link = config.get('gmail', 'google_drive_folder_link')
        self.event_started_message = config.get('gmail', 'event_started_message')
        
        self.presenceMacs = []
        self.network = None
        
        self.ip_addresses = None
        
        try:
            self.presenceMacs = config.get( 'LAN', 'presence_macs' ).split( ',' )
            self.network = config.get( 'LAN', 'network' )
        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            pass
        
        try:
            self.ip_addresses = config.get( 'LAN', 'ip_addresses' )
        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            pass
        
        try:
            self.forceOnStart = config.getint( 'activate-system', 'force_on_start' )
            self.forceOnEnd = config.getint( 'activate-system', 'force_on_end' )
        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            pass
        
        logger.info("All config options set")

    def _create_gdata_client(self):
        """Create a Documents List Client."""
        self.client = gdata.docs.client.DocsClient(source='motion_uploader')
        self.client.http_client.debug = False
        self.client.client_login(self.username, self.password, service=self.client.auth_service, source=self.client.source)
               
    def _get_folder_resource(self):
        try:
            resources = self.client.GetAllResources(uri='https://docs.google.com/feeds/default/private/full/-/folder?title=' + self.folder + '&title-exact=true')
            return resources[0]
        except:
            sys.exit('ERROR: Unable to retrieve resources')
        
    def _send_email(self,msg):
        '''Send an email using the GMail account.'''
        senddate=datetime.strftime(datetime.now(), '%Y-%m-%d')
        m="Date: %s\r\nFrom: %s <%s>\r\nTo: %s\r\nSubject: %s\r\nX-Mailer: My-Mail\r\n\r\n" % (senddate, self.from_name, self.sender, self.recipient, self.subject)
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(self.username, self.password)
        server.sendmail(self.sender, self.recipient, m+msg)
        server.quit()    

    def _upload(self, media_file_path, folder_resource):
        '''Upload the media and return the doc'''
        if media_file_path.endswith('jpg'):
            logger.info( 'Uploading image %s ' % media_file_path )
            try:
                image_file = open(media_file_path)
            except IOError, e:
                sys.exit('ERROR: Unable to open ' + media_file_path + ': ' + e[1])
            
            file_size = os.path.getsize(image_file.name)
            file_type = "image/jpeg"
            uri = folder_resource.get_resumable_create_media_link().href
            uri += '?convert=false'
            uploader = gdata.client.ResumableUploader(self.client, image_file, file_type, file_size, chunk_size=1048576, desired_class=gdata.data.GDEntry)
            doc = uploader.UploadFile(uri, entry=gdata.data.GDEntry(title=atom.data.Title(text=os.path.basename(image_file.name))))
            
        else :
            if media_file_path.endswith('swf'):
                logger.info( 'Uploading video %s ' % media_file_path )
                doc = gdata.docs.data.Resource(type='video', title=os.path.basename(media_file_path))
                media = gdata.data.MediaSource()
                media.SetFileHandle(media_file_path, 'video/avi')
                doc = self.client.CreateResource(doc, media=media, collection=folder_resource)

        return doc
    
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
    
    def upload_media(self, media_file_path, notify):
        if self._system_active() :
            """Upload media file to the specified folder. Then optionally send an email and optionally delete the local file."""
            folder_resource = self._get_folder_resource()
            if not folder_resource:
                raise Exception('Could not find the %s folder' % self.folder)
    
            doc = self._upload(media_file_path, folder_resource)
    
            """Config file has email enable and it is set to true on the command line"""
            if self._email_required(notify):
                media_link = None
                for link in doc.link:
                    if 'video.google.com' in link.href:
                        media_link = link.href
                        break
                # Send an email with the link if found
                msg = self.message
                if media_link:
                    msg += '\n\n' + media_link
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
            exit('Motion Notify - uploads media to Google Drive when network presence indicates nobody is home\n   by Andrew Dean, based on Google Drive Uploader Jeremy Blythe (http://jeremyblythe.blogspot.com)\n\n   Usage: uploader.py {config-file-path} {media-file-path} {send-email (1 if email required, if not, 0)}')
        cfg_path = sys.argv[1]

        vid_path = sys.argv[2]
        if sys.argv[3] == '1' :
            notify = True
        else :
            notify = False
        if not os.path.exists(cfg_path):
            exit('Config file does not exist [%s]' % cfg_path)

        if vid_path == 'None' :
                MotionNotify(cfg_path).send_start_event_email(notify)
                exit('Start event triggered')

        if not os.path.exists(vid_path):
            exit('Video file does not exist [%s]' % vid_path)

        MotionNotify(cfg_path).upload_media(vid_path, notify)
    except gdata.client.BadAuthentication:
        exit('Invalid user credentials given.')
    except gdata.client.Error:
        exit('Login Error')
    except Exception as e:
        exit('Error: [%s]' % e)
