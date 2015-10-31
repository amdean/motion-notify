from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import httplib2
import logging
from datetime import datetime

from oauth2client.client import SignedJwtAssertionCredentials

logger = logging.getLogger('MotionNotify')


class GoogleDriveUploadAction:
    @staticmethod
    def do_event_start_action(config, motion_event):
        logger.info("Motionevent_id:" + motion_event.event_id + " GoogleDriveUploadAction event start")
        GoogleDriveUploadAction.uploadFile(config, motion_event)

    @staticmethod
    def do_event_end_action(config, motion_event):
        logger.info("Motionevent_id:" + motion_event.event_id + " GoogleDriveUploadAction event end")
        GoogleDriveUploadAction.uploadFile(config, motion_event)

    @staticmethod
    def do_action(config, motion_event):
        logger.info("Motionevent_id:" + motion_event.event_id + " GoogleDriveUploadAction event")
        GoogleDriveUploadAction.uploadFile(config, motion_event)

    @staticmethod
    def authenticate(config):
        svc_user_id = config.get('GoogleDriveUploadAction', 'service_user_email')
        svc_scope = "https://www.googleapis.com/auth/drive"
        svc_key_file = config.get('GoogleDriveUploadAction', 'key_file')
        svc_key = open(svc_key_file, 'rb').read()
        gcredentials = SignedJwtAssertionCredentials(svc_user_id, svc_key, scope=svc_scope)
        gcredentials.authorize(httplib2.Http())
        gauth = GoogleAuth()
        gauth.credentials = gcredentials
        logger.debug("GoogleDriveUploadAction authentication complete")
        return gauth

    @staticmethod
    def _get_folder_resource(drive, folder):
        """Find and return the resource whose title matches the given folder."""
        try:
            file_list = drive.ListFile({
                                       'q': "title='{}' and mimeType contains 'application/vnd.google-apps.folder' and trashed=false".format(
                                           folder)}).GetList()
            if len(file_list) > 0:
                return file_list[0]
            else:
                return None
        except IndexError:
            return None
        except:
            return None

    @staticmethod
    def _get_datefolder_resource(drive, formatted_date):
        """Find and return the resource whose title matches the given folder."""
        try:
            file_list = drive.ListFile({
                                       'q': "title='{}' and mimeType contains 'application/vnd.google-apps.folder' and trashed=false".format(
                                           formatted_date)}).GetList()
            if len(file_list) > 0:
                return file_list[0]
            else:
                return None
        except:
            return None

    @staticmethod
    def create_permision(user, role):
        return {
            'value': user,
            'type': "user",
            'role': role
        }

    @staticmethod
    def create_subfolder(drive, folder, sfldname, owner, readers, writers):
        new_folder = drive.CreateFile({'title': '{}'.format(sfldname),
                                       'mimeType': 'application/vnd.google-apps.folder'})
        if folder is not None:
            new_folder['parents'] = [{"id": folder['id']}]

        permissions = []
        owner_permission = GoogleDriveUploadAction.create_permision(owner, "owner")
        write_permissions = [GoogleDriveUploadAction.create_permision(x, "writer") for x in writers]
        read_permissions = [GoogleDriveUploadAction.create_permision(x, "reader") for x in readers]

        permissions.append(owner_permission)
        permissions.extend(write_permissions)
        permissions.extend(read_permissions)

        print('Creating Folder {} with permissions {}'.format(sfldname, permissions))

        new_folder["permissions"] = permissions
        new_folder.Upload()
        logger.info("GoogleDriveUploadAction subfolder created: " + new_folder.__str__())
        return new_folder

    @staticmethod
    def uploadFile(config, motion_event):
        gauth = GoogleDriveUploadAction.authenticate(config)
        drive = GoogleDrive(gauth)
        filename = motion_event.event_id + "_" + motion_event.event_time
        if (motion_event.media_file.endswith(("jpg", "png", "gif", "bmp"))):
            mimeType = "image/" + motion_event.file_type
        else:
            mimeType = "video/" + motion_event.file_type

        folder_name = config.get('GoogleDriveUploadAction', 'folder_name');
        folder_id = config.get('GoogleDriveUploadAction', 'folder');

        # Get Permissions
        owner = config.get('GoogleDriveUploadAction', 'owner')
        writers = filter(lambda x: len(x) > 0,
                         [x.strip() for x in config.get('GoogleDriveUploadAction', 'write_users').split(",")])
        readers = filter(lambda x: len(x) > 0,
                         [x.strip() for x in config.get('GoogleDriveUploadAction', 'read_users').split(",")])
        writers.append(owner)

        # Check Root Folder Exists
        folder_resource = GoogleDriveUploadAction._get_folder_resource(drive, folder_name)
        if not folder_resource:
            logger.info('Creating Folder {}'.format(folder_name))
            folder_resource = GoogleDriveUploadAction.create_subfolder(drive, None, folder_name, owner, readers,
                                                                       writers)
            # raise Exception('Could not find the %s folder' % self.folder)

        logger.debug(
            "Motionevent_id:" + motion_event.event_id + 'Using Folder {} {}'.format(folder_name, folder_resource['id']))

        # Check Date Folder Exists & Create / Use as needed
        senddate = datetime.strftime(datetime.now(), config.get('GoogleDriveUploadAction', 'dateformat'))
        datefolder_resource = GoogleDriveUploadAction._get_datefolder_resource(drive, senddate)
        if not datefolder_resource:
            logger.info('Creating Date Folder {}'.format(senddate))
            datefolder_resource = GoogleDriveUploadAction.create_subfolder(drive, folder_resource, senddate, owner,
                                                                           readers, writers)

        logger.debug("Motionevent_id:" + motion_event.event_id + ' Using Date Folder {} {}'.format(senddate,
                                                                                                 datefolder_resource[
                                                                                                     'id']))

        # Create File in Date Folder
        gfile = drive.CreateFile({'title': filename, 'mimeType': mimeType,
                                  "parents": [{"kind": "drive#fileLink", "id": datefolder_resource['id']}]})

        gfile.Upload()

        logger.debug("Motionevent_id:" + motion_event.event_id + 'Uploaded File  {} {}'.format(filename, gfile['id']))

        return '\n\nhttps://drive.google.com/file/d/' + gfile['id'] + '/view?usp=sharing'
