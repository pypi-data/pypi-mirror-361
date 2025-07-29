#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : pdn.py
@Author : yell
@Desc : pdn framework
'''
from engine.base import EngineBase

class EnginePDN(EngineBase):
    """pdn framework"""
    def __init__(self, dir_workspace : str):
        super().__init__(dir_workspace)
        
    
    def run(self):
        pass