__author__ = 'adean'

import os
import logging.handlers

logger = logging.getLogger('MotionNotify')

class DeleteMediaFileAction:
    @staticmethod
    def doEventStartAction(config, motion_event):
        logger.info("MotionEventId:" + motion_event.eventId.__str__() + "Deleting: %s", motion_event.mediaFile)
        DeleteMediaFileAction.delete_file(motion_event.mediaFile)

    @staticmethod
    def doEventEndAction(config, motion_event):
        logger.info("MotionEventId:" + motion_event.eventId.__str__() + "Deleting: %s", motion_event.mediaFile)
        DeleteMediaFileAction.delete_file(motion_event.mediaFile)

    @staticmethod
    def doAction(config, motion_event):
        logger.info("MotionEventId:" + motion_event.eventId.__str__() + "Deleting: %s", motion_event.mediaFile)
        DeleteMediaFileAction.delete_file(motion_event.mediaFile)

    @staticmethod
    def delete_file(file_path):
        os.remove(file_path)
