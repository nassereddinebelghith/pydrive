#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import json
import os.path

from mimetypes import MimeTypes
from googleapiclient.http import MediaFileUpload
from zdrive import DriveAPI


class Uploader(DriveAPI):
    def __init__(self):
        super(Uploader, self).__init__()
        self.__default_depth = 5

    @staticmethod
    def __isValidDir(path):
        """
        checks whether the given path
        exists in the directory or not
        :type path: string
        :param path: the path to check
        :return: 1 if path exists, 0 if it doesn't
        """

        return os.path.isdir(path)

    def createFolder(self, name, parentId=None):
        try:
            # Check if folder already exists
            query = "mimeType='application/vnd.google-apps.folder' and trashed=false and name='{}'".format(name)
            if parentId is not None:
                query += " and parents='{}'".format(parentId)

            response = self.service.files().list(q=query, spaces='drive', fields='nextPageToken, files(id, name)').execute()

            # If folder exists, return its ID
            if len(response.get('files', [])) > 0:
                folder_id = response['files'][0]['id']
                print('\t -> Folder already exists: {0} with ID: {1}'.format(name, folder_id))
                return folder_id

            # If folder does not exist, create a new one and return its ID
            else:
                file_metadata = {
                    'name': name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                if parentId is not None:
                    file_metadata["parents"] = [parentId]

                file = self.service.files().create(body=file_metadata,
                                                   fields='id').execute()

                folder_id = file.get('id')

                print('\t -> Created folder: {0} with ID: {1}'.format(name, folder_id))
                return folder_id

        except Exception as e:
            raise Exception(e)


    def uploadFile(self, filePath, parentId):
        try:
            file_name = os.path.basename(filePath)
            mimetype = MimeTypes().guess_type(file_name)[0]

            file_metadata = {'name': file_name}

            if parentId is not None:
                file_metadata["parents"] = [parentId]

            media = MediaFileUpload(filePath,
                                    mimetype=mimetype,
                                    resumable=True)

            file = self.service.files().create(body=file_metadata,
                                               media_body=media,
                                               fields='id').execute()

            file_id = file.get('id')
            print('\t -> File {0} uploaded successfully! ID: {1}'.format(file_name, file_id))
            return file_id
        except Exception as e:
            raise Exception(e)

    def __upload_folder(self, folder_path, current_depth, max_depth, parent_id=None):
        try:
            # check depth
            if current_depth > max_depth:
                return {}

            print("Uploading folder {}".format(folder_path))

            # get files and folders
            root_files = []
            root_folders = []
            for (_, dirs, files) in os.walk(folder_path, topdown=True):
                root_files.extend(files)
                root_folders.extend(dirs)
                break

            # upload files
            files_upload_dict = self.__upload_files(folder_path, root_files, parent_id)

            # recursively create and upload folder
            folders_upload_dict = {}

            current_depth += 1
            for folder in root_folders:
                folder_id = self.createFolder(folder, parent_id)
                full_path = os.path.join(folder_path, folder)
                print("\t -> Stepping inside folder {0}".format(full_path))
                folder_result_dict = self.__upload_folder(full_path, current_depth, max_depth, folder_id)
                folder_result_dict["id"] = folder_id
                folders_upload_dict[full_path] = folder_result_dict

            print("Success! Uploaded folder {} ".format(folder_path))

            result = {
                'files': files_upload_dict,
                'folders': folders_upload_dict
            }

            return result
        except Exception as e:
            raise Exception(e)

    def uploadFolder(self, folderPath, max_depth=None, parentId=None):
        try:
            if not self.__isValidDir(folderPath):
                raise Exception("Not a valid folder path {0}".format(folderPath))

            if max_depth is None:
                max_depth = self.__default_depth

            upload_status = self.__upload_folder(folderPath, 1, max_depth, parentId)
            return json.dumps(upload_status, indent=4)
        except Exception as e:
            raise Exception(e)

		

    def __upload_files(self, folder_path, root_files, parent_id=None):
        try:
            if len(root_files) == 0:
                return {}
            uploaded_files = {}
            for file in root_files:
                file_path = os.path.join(folder_path, file)
                file_id = self.uploadFile(file_path, parent_id)
                uploaded_files[file_path] = file_id
            return uploaded_files
        except Exception as e:
            print(str(e))
            return {}
        


    def get_folder_id(folder_name, parent_folder_name):
        """
        Gets the folder ID based on a given folder name located in another folder.
        
        Args:
            folder_name (str): The name of the folder to search for.
            parent_folder_name (str): The name of the parent folder where to search for the folder.
        
        Returns:
            str: The folder ID if found, None otherwise.
        """
        try:
            service = build('drive', 'v3')
            
            # Search for the parent folder ID based on the parent folder name
            query = f"name='{parent_folder_name}' and mimeType='application/vnd.google-apps.folder'"
            response = service.files().list(q=query, fields='nextPageToken, files(id)').execute()
            parent_folder_id = None
            for folder in response.get('files', []):
                if folder['id']:
                    parent_folder_id = folder['id']
                    break
            
            if parent_folder_id is not None:
                # Search for the folder ID based on the folder name and parent folder ID
                query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and parents in '{parent_folder_id}'"
                response = service.files().list(q=query, fields='nextPageToken, files(id)').execute()
                folder_id = None
                for folder in response.get('files', []):
                    if folder['id']:
                        folder_id = folder['id']
                        break
                return folder_id
            else:
                print(f'Parent folder with name "{parent_folder_name}" not found.')
                return None
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
     

    
    def delete_folder(self, folder_name, parent_folder_id=None):
        """
        Deletes a folder with the given name from the parent folder with the given ID in Google Drive.
        If parent_folder_id is not provided, the root folder will be used as the parent folder.
        """
        try:
            # Get the parent folder ID
            if parent_folder_id is None:
                parent_folder_id = self.root_folder_id
            
            # Check if parent folder exists
            if parent_folder_id is None:
                print(f"Parent folder ID '{parent_folder_id}' does not exist")
                return
            
            # Search for the folder to delete in the parent folder
            query = f"name = '{folder_name}' and parents in '{parent_folder_id}' and mimeType = 'application/vnd.google-apps.folder'"
            response = self.service.files().list(q=query, fields='files(id)').execute()
            folders = response.get('files', [])
            
            if not folders:
                print(f"Folder '{folder_name}' does not exist in parent folder ID '{parent_folder_id}'")
                return
            elif len(folders) > 1:
                print(f"Multiple folders with name '{folder_name}' found in parent folder ID '{parent_folder_id}', please specify a unique folder name")
                return
            
            folder_id = folders[0]['id']
            
            # Delete the folder
            self.service.files().delete(fileId=folder_id).execute()
            
            print(f"Deleted folder '{folder_name}' from parent folder ID '{parent_folder_id}' in Google Drive")
        
        except Exception as e:
            print(f"Error deleting folder '{folder_name}': {str(e)}")