from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import logging.handlers

logger = logging.getLogger('MotionNotify')


class GoogleDriveCleanupAction:
    @staticmethod
    def do_event_start_action(config, motion_event):
        logger.info("Motionevent_id:" + motion_event.event_id + " GoogleDriveCleanupAction event start")
        motion_event.upload_url = GoogleDriveCleanupAction.cleanup(config)

    @staticmethod
    def do_event_end_action(config, motion_event):
        logger.info("Motionevent_id:" + motion_event.event_id + " GoogleDriveCleanupAction event end")
        motion_event.upload_url = GoogleDriveCleanupAction.cleanup(config, motion_event)

    @staticmethod
    def do_action(config, motion_event):
        logger.info("Motionevent_id:" + motion_event.event_id + " GoogleDriveCleanupAction event")
        motion_event.upload_url = GoogleDriveCleanupAction.cleanup(config)

    @staticmethod
    def cleanup(config):
        logger.info("GoogleDriveCleanupAction event")
