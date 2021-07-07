# -*- coding: utf-8 -*-


from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class GoogleAuthentication():
    
    def __init__(self):
        self.gauth = GoogleAuth()
        self.gauth.LocalWebserverAuth() # client_secrets.json need to be in the same directory as the script
        self.drive = GoogleDrive(self.gauth)
        
    def list_files_in_root(self):
        fileList = self.drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        for file in fileList:
          print('Title: %s, ID: %s' % (file['title'], file['id']))
    
    
    def create_file(self, file_name):
        file = self.drive.CreateFile({"mimeType": "video/mp4",
                                  "parents": [{"id": 'your_folder_id'}],
                                  "title":f"{file_name}"})
        file.Upload() # Update content of the file.
        file.SetContentFile(f'{file_name}')
        file.Upload() # Upload the file.  
