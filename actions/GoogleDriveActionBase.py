from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import httplib2
import logging.handlers
from datetime import datetime
import fcntl, os
import sys

from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger('MotionNotify')


class GoogleDriveActionBase:

    @staticmethod
    def authenticate(config):
        logger.debug("GoogleDriveAction starting authentication")
        svc_user_id = config.config_obj.get('GoogleDriveUploadAction', 'service_user_email')
        svc_scope = "https://www.googleapis.com/auth/drive"
        svc_key_file = config.config_obj.get('GoogleDriveUploadAction', 'key_file')
        gcredentials = ServiceAccountCredentials.from_p12_keyfile(svc_user_id, svc_key_file, scopes=svc_scope)
        gcredentials.authorize(httplib2.Http())
        gauth = GoogleAuth()
        gauth.credentials = gcredentials
        logger.debug("GoogleDriveUploadAction authentication complete")
        return gauth

    @staticmethod
    def _get_folder_resource(drive, folder_name, folder_id):
        """Find and return the resource whose title matches the given folder."""
        try:
            myfile = drive.CreateFile({'id': folder_id})
            logger.debug("Found Parent Folder title: {}, mimeType: {}".format(myfile['title'], myfile['mimeType']))
            return myfile

            # file_list = drive.ListFile({'q': "title='{}' and mimeType contains 'application/vnd.google-apps.folder' and trashed=false".format(folder_name)}).GetList()
            # if len(file_list) > 0:
            #    return file_list[0]
            # else:
            #    return None
        except IndexError:
            return None
        except:
            return None

    @staticmethod
    def _get_datefolder_resource(drive, formatted_date, parent_id):
        """Find and return the resource whose title matches the given folder."""
        try:
            file_list = drive.ListFile({
                'q': "title='{}' and '{}' in parents and mimeType contains 'application/vnd.google-apps.folder' and trashed=false".format(
                    formatted_date, parent_id)}).GetList()
            if len(file_list) > 0:
                return file_list[0]
            else:
                return None
        except:
            return None
