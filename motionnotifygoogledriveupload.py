from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import httplib2
import logging.handlers
from datetime import datetime

from oauth2client.client import SignedJwtAssertionCredentials

logger = logging.getLogger( 'MotionNotify.GoogleUpload')
#logger.setLevel( logging.DEBUG )

class MotionNotifyGoogleUpload:
    @staticmethod
    def authenticate(config):
        logger.debug("OAuth2 Authentication - Starting")
        svc_user_id = config.get('drive', 'service_user_email')
        svc_scope = "https://www.googleapis.com/auth/drive"
        svc_key_file = config.get('drive', 'key_file')
        svc_key = open(svc_key_file, 'rb').read()
        gcredentials = SignedJwtAssertionCredentials(svc_user_id, svc_key, scope=svc_scope)
        gcredentials.authorize(httplib2.Http())
        gauth = GoogleAuth()
        gauth.credentials = gcredentials
        logger.debug("OAuth2 Authentication - Complete")
        return gauth

    @staticmethod
    def _get_folder_resource(drive,folder_name,folder_id):
        """Find and return the resource whose title matches the given folder."""
        try:
            myfile = drive.CreateFile({'id': folder_id})
            logger.debug ("Found Parent Folder title: {}, mimeType: {}".format(myfile['title'], myfile['mimeType']) )
            return  myfile

            #file_list = drive.ListFile({'q': "title='{}' and mimeType contains 'application/vnd.google-apps.folder' and trashed=false".format(folder_name)}).GetList()
            #if len(file_list) > 0:
            #    return file_list[0]
            #else:
            #    return None
        except IndexError:
            return None
        except:
            return None

    @staticmethod
    def _get_datefolder_resource(drive,formatted_date, parent_id):
        """Find and return the resource whose title matches the given folder."""
        try:
            file_list = drive.ListFile({'q': "title='{}' and '{}' in parents and mimeType contains 'application/vnd.google-apps.folder' and trashed=false".format(formatted_date,parent_id)}).GetList()
            if len(file_list) > 0:
                return file_list[0]
            else:
                return None
        except:
            return None

    @staticmethod
    def create_permision(user,role):
        return {
            'value': user,
            'type': "user",
            'role': role
        }

    @staticmethod
    def create_subfolder(drive,folder,sfldname,owner,readers, writers):
        new_folder = drive.CreateFile({'title':'{}'.format(sfldname),
                                   'mimeType':'application/vnd.google-apps.folder'})
        if folder is not None:
            new_folder['parents'] = [{"kind": "drive#fileLink","id": folder['id']}]

        permissions = []
        owner_permission = MotionNotifyGoogleUpload.create_permision(owner,"owner")
        write_permissions = [MotionNotifyGoogleUpload.create_permision(x,"owner") for x in writers]
        read_permissions  = [MotionNotifyGoogleUpload.create_permision(x,"reader") for x in readers]

        permissions.append(owner_permission)
        permissions.extend(write_permissions)
        permissions.extend(read_permissions)

        logger.debug('Creating Folder {} with permissions {}'.format(sfldname, permissions))

        new_folder["permissions"] = permissions
        new_folder.Upload()
        return new_folder


    @staticmethod
    def upload(media_file_path, filename, config, mime):
        gauth = MotionNotifyGoogleUpload.authenticate(config)
        drive = GoogleDrive(gauth)


        folder_name = config.get('drive', 'folder_name');
        folder_id = config.get('drive', 'folder');

        # Get Permissions
        owner = config.get('gmail','user')
        writers = filter(lambda x:len(x)>0, [x.strip() for x in config.get('drive','write_users').split(",")] )
        readers = filter(lambda x:len(x)>0, [x.strip() for x in config.get('drive','read_users').split(",")] )
        #Keep Owner Seperate # Remove Just in case
        if owner in writers:
            writers.remove(owner);

        # Check Root Folder Exists
        folder_resource = MotionNotifyGoogleUpload._get_folder_resource(drive,folder_name,folder_id)
        if not folder_resource:
            #logger.info('Creating Folder {}'.format(folder_name))
            # This seemed to create lots of folders I'd no access to, so changing to an Exception
            # Might need some way to set it to the root of the gmail user and not the service user
            #folder_resource = MotionNotifyGoogleUpload.create_subfolder(drive,None,folder_name,owner,readers, writers)
            logger.error("Could not find the {} folder {}".format(folder_name,folder_id) )
            raise Exception("Could not find the {} folder {}".format(folder_name,folder_id) )

        logger.debug('Using Folder {} {}'.format(folder_name,folder_resource['id']))

        # Check Date Folder Exists & Create / Use as needed
        senddate=(datetime.strftime(datetime.now(), config.get('drive', 'dateformat')))
        datefolder_resource = MotionNotifyGoogleUpload._get_datefolder_resource(drive,senddate,folder_resource['id'])
        if not datefolder_resource:
            logger.info('Creating Date Folder {}'.format(senddate))
            datefolder_resource = MotionNotifyGoogleUpload.create_subfolder(drive,folder_resource,senddate,owner,readers, writers)

        logger.debug('Using Date Folder {} {}'.format(senddate,datefolder_resource['id']))

        # Create File in Date Folder
        gfile = drive.CreateFile({'title': filename, 'mimeType': mime,
                                  "parents": [{"kind": "drive#fileLink", "id": datefolder_resource['id']}]})
        gfile.SetContentFile(media_file_path)
        gfile.Upload()

        logger.debug('Uploaded File  {} {}'.format(filename,gfile['id']))

        return '\n\nhttps://drive.google.com/file/d/' + gfile['id'] + '/view?usp=sharing'
