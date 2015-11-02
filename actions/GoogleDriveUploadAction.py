from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import httplib2
import logging.handlers
from datetime import datetime
import fcntl, os
import sys

from oauth2client.client import SignedJwtAssertionCredentials

LOCK_FILENAME = "/var/tmp/motion-notify.lock.pid"
logger = logging.getLogger('MotionNotify')


class GoogleDriveUploadAction:
    @staticmethod
    def do_event_start_action(config, motion_event):
        logger.info("Motionevent_id:" + motion_event.event_id + " GoogleDriveUploadAction event start")
        GoogleDriveUploadAction.upload(config, motion_event)

    @staticmethod
    def do_event_end_action(config, motion_event):
        logger.info("Motionevent_id:" + motion_event.event_id + " GoogleDriveUploadAction event end")
        GoogleDriveUploadAction.upload(config, motion_event)

    @staticmethod
    def do_action(config, motion_event):
        logger.info("Motionevent_id:" + motion_event.event_id + " GoogleDriveUploadAction event")
        GoogleDriveUploadAction.upload(config, motion_event)

    @staticmethod
    def authenticate(config):
        logger.debug("GoogleDriveUploadAction starting authentication")
        svc_user_id = config.config_obj.get('GoogleDriveUploadAction', 'service_user_email')
        svc_scope = "https://www.googleapis.com/auth/drive"
        svc_key_file = config.config_obj.get('GoogleDriveUploadAction', 'key_file')
        svc_key = open(svc_key_file, 'rb').read()
        gcredentials = SignedJwtAssertionCredentials(svc_user_id, svc_key, scope=svc_scope)
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
            new_folder['parents'] = [{"kind": "drive#fileLink", "id": folder['id']}]

        permissions = []
        owner_permission = GoogleDriveUploadAction.create_permision(owner, "owner")
        write_permissions = [GoogleDriveUploadAction.create_permision(x, "owner") for x in writers]
        read_permissions = [GoogleDriveUploadAction.create_permision(x, "reader") for x in readers]

        permissions.append(owner_permission)
        permissions.extend(write_permissions)
        permissions.extend(read_permissions)

        logger.debug('Creating Folder {} with permissions {}'.format(sfldname, permissions))

        new_folder["permissions"] = permissions
        new_folder.Upload()
        return new_folder

    @staticmethod
    def upload(config, motion_event):
        logger.debug("GoogleDriveUploadAction starting upload")
        mutex_enabled = config.config_obj.get('GoogleDriveUploadAction', 'mutex-enabled')
        if mutex_enabled:
            f = GoogleDriveUploadAction.lock(motion_event.media_file)

        gauth = GoogleDriveUploadAction.authenticate(config)
        drive = GoogleDrive(gauth)

        folder_name = config.config_obj.get('GoogleDriveUploadAction', 'folder_name')
        folder_id = config.config_obj.get('GoogleDriveUploadAction', 'folder')

        # Get Permissions
        owner = config.config_obj.get('GoogleDriveUploadAction', 'owner')
        writers = filter(lambda x: len(x) > 0, [x.strip() for x in
                                                config.config_obj.get('GoogleDriveUploadAction', 'write_users').split(
                                                    ",")])
        readers = filter(lambda x: len(x) > 0,
                         [x.strip() for x in config.config_obj.get('GoogleDriveUploadAction', 'read_users').split(",")])
        # Keep Owner Seperate # Remove Just in case
        if owner in writers:
            writers.remove(owner);

        # Check Root Folder Exists
        folder_resource = GoogleDriveUploadAction._get_folder_resource(drive, folder_name, folder_id)
        if not folder_resource:
            # logger.info('Creating Folder {}'.format(folder_name))
            # folder_resource = MotionNotifyGoogleUpload.create_subfolder(drive,None,folder_name,owner,readers, writers)
            #
            # This seemed to create lots of folders I'd no access to, so changing to an Exception
            # Might need some way to set it to the root of the gmail user and not the service user

            logger.error("Could not find the {} folder {}".format(folder_name, folder_id))
            raise Exception("Could not find the {} folder {}".format(folder_name, folder_id))

        logger.debug('Using Folder {} {}'.format(folder_name, folder_resource['id']))

        # Check Date Folder Exists & Create / Use as needed
        senddate = (datetime.strftime(datetime.now(), config.config_obj.get('GoogleDriveUploadAction', 'dateformat')))
        datefolder_resource = GoogleDriveUploadAction._get_datefolder_resource(drive, senddate, folder_resource['id'])
        if not datefolder_resource:
            logger.info('Creating Date Folder {}'.format(senddate))
            datefolder_resource = GoogleDriveUploadAction.create_subfolder(drive, folder_resource, senddate, owner,
                                                                           readers, writers)

        logger.debug('Using Date Folder {} {}'.format(senddate, datefolder_resource['id']))

        # Create File in Date Folder
        gfile = drive.CreateFile({'title': motion_event.get_upload_filename(), 'mimeType': motion_event.get_mime_type(),
                                  "parents": [{"kind": "drive#fileLink", "id": datefolder_resource['id']}]})
        gfile.SetContentFile(motion_event.media_file)
        gfile.Upload()

        logger.debug(
            "Motionevent_id:" + motion_event.event_id + ' GoogleDriveUploadAction Uploaded File  {} {}'.format(
                motion_event.get_upload_filename(),
                gfile[
                    'id']))

        if mutex_enabled:
            GoogleDriveUploadAction.unlock(f, motion_event.media_file)

        return '\n\nhttps://drive.google.com/file/d/' + gfile['id'] + '/view?usp=sharing'

    @staticmethod
    def lock(media_file_path):
        pid = str(os.getpid())
        f = open(LOCK_FILENAME, 'w')
        logger.debug("Trying to Get Lock for upload of {}, pid {}".format(media_file_path, pid))
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            logger.warn("Can't get Lock for upload of {}, pid {}, blocking".format(media_file_path, pid))
            fcntl.flock(f, fcntl.LOCK_EX)
            logger.debug("Got Lock for upload of {}, pid {}, blocking".format(media_file_path, pid))

        try:
            f.write("%s\n" % pid)
            logger.debug("Writing PID for upload of {}, pid {}, to file {}".format(media_file_path, pid, LOCK_FILENAME))
        except IOError:
            logger.error(
                "Unable to write PID for upload of {}, pid {}, to file {}".format(media_file_path, pid, LOCK_FILENAME))
            logger.error("Aborting")
            sys.exit(1)
        return f

    @staticmethod
    def unlock(f, media_file_path):
        fcntl.flock(f, fcntl.LOCK_UN)
        if (logger.isEnabledFor(logging.DEBUG)):
            logger.debug("Unlock for upload of {}, pid {}, blocking".format(media_file_path, os.getpid()))
