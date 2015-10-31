#!/usr/bin/python2
'''
Created on 18th July 2015

@author: Andrew Dean

Motion Notify v0.3 - uploads images and video to Google Drive and sends notification via email.
Detects whether someone is home by checking the local network for an IP address or MAC address and only sends email if nobody is home.
Allows hours to be defined when the system will be active regardless of network presence.

Sends an email to the user at that start of an event and uploads images throughout the event.
At the end of an event the video is uploaded to Google Drive and a link is emailed to the user.
Files are deleted once they are uploaded.

Originally based on the Google Drive uploader developed by Jeremy Blythe (http://jeremyblythe.blogspot.com) and pypymotion (https://github.com/7AC/pypymotion) by Wayne Dyck
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

import os.path
import sys
import logging.handlers
import traceback
from objects import motion_event
from objects import config
from objects.enums import EventType
from utils import utils

logger = logging.getLogger('MotionNotify')
hdlr = logging.handlers.RotatingFileHandler('/var/tmp/motion-notify.log',
                                            maxBytes=1048576,
                                            backupCount=3)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


def loggerExceptHook(t, v, tb):
    logger.error(traceback.format_exception(t, v, tb))


sys.excepthook = loggerExceptHook


class MotionNotify:
    def handle_event(self):
        self.is_system_active = self.config.detector_rule_set.get_status_for_detector_rule_set(self, config)
        actions_for_event = self.motion_event.get_actions_for_event(self.config, self.is_system_active)
        for action in actions_for_event:
            logger.info(
                "Handling action: " + action + " for event ID " + self.motion_event.eventId + " with event_type " + self.motion_event.event_type)
            klass = utils.Utils.reflect_class_from_classname('actions', action)
            if self.motion_event.event_type == EventType.EventType.on_event_start:
                klass.do_event_start_action(config, motion_event)
            elif self.motion_event.event_type == EventType.EventType.on_picture_save:
                klass.doOnPictureSaveAction(config, motion_event)
            elif self.motion_event.event_type == EventType.EventType.on_movie_end:
                klass.doOnMovieEndAction(config, motion_event)

    def __init__(self, config, motion_event):
        self.config = config
        self.motion_event = motion_event
        self.is_system_active = False
        self.handle_event()


if __name__ == '__main__':
    logger.info("Motion Notify script started")
    try:

        if len(sys.argv) < 6:
            exit(
                'Motion Notify - Usage: uploader.py {config-file-path} {media-file-path} {event-type on_event_start, on_picture_save or on_movie_end} {timestamp} {event_id} {filetype} ')

        cfg_path = sys.argv[1]
        if not os.path.exists(cfg_path):
            exit('Config file does not exist [%s]' % cfg_path)

        motion_event = motion_event.MotionEvent(sys.argv[2], EventType[sys.argv[3]], sys.argv[4], sys.argv[5],
                                                sys.argv[6])

        MotionNotify(config.Config(cfg_path), motion_event)
    except Exception as e:
        exit('Error: [%s]' % e)
