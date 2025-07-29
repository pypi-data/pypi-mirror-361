#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@file         : main.py
@author       : Yell
@brief        : 
@version      : 0.1
@date         : 2024-03-02 09:10:20
'''

import gzip

from utility.json_parser import JsonParser

class ReportJson():
    """basic class for transfer report to json"""
    def __init__(self, report_path : str, json_path : str):
        self.report_path = report_path
        self.json_path = json_path
        self.report_parser = None
        self.json_parser = None
        
    def get_report_parser(self):
        return self.report_parser
    
    def get_json_data(self):
        return self.json_parser.get_json_data()
    
    def read(self):
        # read report file
        with gzip.open(self.report_path, 'rb') as f:
            self.report_parser = f.read()
            
        # read json file
        self.json_parser = JsonParser(self.json_path)
        self.json_parser.read_create()
    
    def writeJson(self):
        return self.json_parser.write()