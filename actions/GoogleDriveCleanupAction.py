from pydrive.drive import GoogleDrive
import GoogleDriveActionBase
from datetime import datetime, timedelta

import logging.handlers

logger = logging.getLogger('MotionNotify')


class GoogleDriveCleanupAction:
    @staticmethod
    def do_event_start_action(config, motion_event):
        logger.info("Motionevent_id:" + motion_event.event_id + " GoogleDriveCleanupAction event start")
        GoogleDriveCleanupAction.cleanup(config)

    @staticmethod
    def do_event_end_action(config, motion_event):
        logger.info("Motionevent_id:" + motion_event.event_id + " GoogleDriveCleanupAction event end")
        GoogleDriveCleanupAction.cleanup(config)

    @staticmethod
    def do_action(config, motion_event):
        logger.info("Motionevent_id:" + motion_event.event_id + " GoogleDriveCleanupAction event")
        GoogleDriveCleanupAction.cleanup(config)

    @staticmethod
    def cleanup(config):
        gauth = GoogleDriveActionBase.GoogleDriveActionBase.authenticate(config)
        drive = GoogleDrive(gauth)
        retain_from_date = datetime.today() - timedelta(days=int(config.config_obj.get('GoogleDriveUploadAction', 'file_retention_days')))

        file_list = drive.ListFile({'q': "'" + config.config_obj.get('GoogleDriveUploadAction', 'folder') + "' in parents and modifiedDate<'"
+ retain_from_date.strftime("%Y-%m-%d") + "'", 'maxResults': 1000}).GetList()
        print(file_list.__sizeof__())
        for file1 in file_list:
            logger.debug('GoogleDriveUploadAction Removing: title: %s, id: %s, createdDate: %s, parents: %s' % (file1['title'], file1['id'], file1['createdDate'], file1['parents']))
            file1.Delete()





