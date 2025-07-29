#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : flow_manager.py
@Author : yell
@Desc : Manage flow
'''
from engine.base import EngineBase

class EngineDatabase(EngineBase):
    """Manage flow"""
    def __init__(self, dir_workspace : str):
        super().__init__(dir_workspace)
        
    
    def run(self):
        pass