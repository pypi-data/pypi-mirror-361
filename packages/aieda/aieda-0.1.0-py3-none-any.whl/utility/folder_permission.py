#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : folder_permission.py
@Author : yell
@Desc : change folder authorization
'''

######################################################################################
# import ai-eda as root

######################################################################################
import os

class FolderPermissionManager():
    def __init__(self, folder: str):
        self.directory = folder

    def enable_read_and_write(self):
        self.recursive(self.directory)
            
    def recursive(self, directory : str):
        for root, dirs, files in os.walk(directory):
            self.try_chmod(root)
                
            for file in files:
                self.try_chmod(os.path.join(root, file))
                
            for dir in dirs:
                self.try_chmod(os.path.join(root, dir))
                self.recursive(dir)
                
    def try_chmod(self, path):
        try:
            os.chmod(path, 0o777)
        except Exception as e:
            pass
            # print("chmod error for path : " + path)
            
                
                
        

