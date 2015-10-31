__author__ = 'adean'

import os
import logging.handlers

logger = logging.getLogger('DeleteMediaFileAction')


class DeleteMediaFileAction:
    @staticmethod
    def doEventStartAction(config, motion_event):
        DeleteMediaFileAction.delete_file(motion_event.mediaFile)

    @staticmethod
    def doEventEndAction(config, motion_event):
        DeleteMediaFileAction.delete_file(motion_event.mediaFile)

    @staticmethod
    def doAction(config, motion_event):
        DeleteMediaFileAction.delete_file(motion_event.mediaFile)

    @staticmethod
    def delete_file(file_path):
        logger.info("Deleting: %s", file_path)
        os.remove(file_path)
