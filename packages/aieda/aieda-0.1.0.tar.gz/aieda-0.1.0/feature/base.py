#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : base.py
@Author : yell
@Desc : feature base 
'''

from settings.setting import Settings
from workspace.path import WorkspacePath
from database.enum import EdaTool, FeatureOption
from flow.flow_db import DbFlow

class FeatureBase():
    """feature base"""
    
    def __init__(self, dir_workspace : str, dir_resource : str = "", eda_tool : EdaTool = EdaTool.IEDA, 
                 feature_option : FeatureOption = FeatureOption.summary, flow : DbFlow = None,
                 input_def : str = None, input_verilog : str = None):
        self.dir_workspace = dir_workspace
        self.dir_resource = dir_resource
        self.eda_tool = eda_tool
        self.feature_option = feature_option
        self.flow = flow
        self.input_def = input_def
        self.input_verilog = input_verilog    
        
        self.workspace = WorkspacePath(dir_workspace)
        
    def generate(self, feature_option : FeatureOption = FeatureOption.NoFeature, reload : bool = False):
        # reset feature option
        if(feature_option != FeatureOption.NoFeature):
            self.feature_option = feature_option
            
        if(self.eda_tool == EdaTool.IEDA):
            return self.generate_db_ieda(reload = reload)
            
        if(self.eda_tool == EdaTool.INNOVUS):
            return self.generate_db_innovus()
        
    def get_db(self, feature_option : FeatureOption = FeatureOption.NoFeature):
        # reset feature option
        if(feature_option != FeatureOption.NoFeature):
            self.feature_option = feature_option
            
        if(self.eda_tool == EdaTool.IEDA):
            return self.get_db_ieda()
            
        if(self.eda_tool == EdaTool.INNOVUS):
            return self.get_db_innovus()