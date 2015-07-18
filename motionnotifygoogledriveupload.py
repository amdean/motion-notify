from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import httplib2

from oauth2client.client import SignedJwtAssertionCredentials


class MotionNotifyGoogleUpload:
    @staticmethod
    def authenticate(config):
        svc_user_id = config.get('drive', 'service_user_email')
        svc_scope = "https://www.googleapis.com/auth/drive"
        svc_key_file = config.get('drive', 'key_file')
        svc_key = open(svc_key_file, 'rb').read()
        gcredentials = SignedJwtAssertionCredentials(svc_user_id, svc_key, scope=svc_scope)
        gcredentials.authorize(httplib2.Http())
        gauth = GoogleAuth()
        gauth.credentials = gcredentials
        return gauth

    @staticmethod
    def upload(media_file_path, filename, config, mime):
        gauth = MotionNotifyGoogleUpload.authenticate(config)
        drive = GoogleDrive(gauth)

        gfile = drive.CreateFile({'title': filename, 'mimeType': mime,
                                  "parents": [{"kind": "drive#fileLink", "id": config.get('drive', 'folder')}]})
        gfile.SetContentFile(media_file_path)
        gfile.Upload()
        return '\n\nhttps://drive.google.com/file/d/' + gfile['id'] + '/view?usp=sharing'
