from pydrive.auth import GoogleAuth

import httplib2
import logging.handlers

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
