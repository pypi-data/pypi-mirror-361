#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : base.py
@Author : yell
@Desc : an EDA engine framework 
'''
import sys 
# sys.path.insert(0, r'/home/yexinyu/AiEDA/engine/base.py')
# sys.path.insert(0, r'/home/yexinyu/AiEDA')

from database.enum import EdaTool, FlowStep, TaskOption, FeatureOption
from settings.setting import Settings
from workspace.path import WorkspacePath
from flow.flow_db import DbFlow
from feature.io import FeatureIO
from typing import List


class EngineResult(object):
    """data structure for output"""
    intput_def : str = ""
    input_verilog : str = ""
    output_def : str = ""
    output_verilog : str = ""
    output_gds = ""
    output_features = {}
    output_logs = {}
    output_reports = {}
    
    def print_data(self):
        print(self.intput_def)
        print(self.input_verilog)
        print(self.output_def)
        print(self.output_verilog)
        print(self.output_gds)
        print(self.output_features)
        print(self.output_logs)
        print(self.output_reports)

class EngineBase():
    """engine base"""
    
    def __init__(self, dir_workspace : str, dir_resource : str = "",
                 eda_tool : EdaTool = EdaTool.IEDA, task : TaskOption = TaskOption.RUN_EDA, output_spef : str = None,
                 input_def : str = None, input_verilog : str = None, 
                 output_def : str = None, output_verilog : str = None,
                 pre_step : DbFlow = None, step : DbFlow = None, first_arg : str = "starrc", input_params : List[str] = []):
        self.dir_workspace = dir_workspace
        self.dir_resource = dir_resource
        self.eda_tool = eda_tool
        self.task = task
        self.input_def = input_def
        self.input_verilog = input_verilog
        self.output_def = output_def
        self.output_verilog = output_verilog
        self.pre_step = pre_step
        self.step : DbFlow = step
        self.first_arg = first_arg
        self.input_params = input_params
        self.output_spef = output_spef
        
        if(self.step != None):
            self.step.pre_flow = pre_step

        self.workspace = WorkspacePath(dir_workspace)
        self.result = EngineResult()
        
    def build_path(self):   
        """rebuild path by flow step"""
        design_name = self.workspace.json_workspace.design
        
        # reset input def
        if(self.input_def == None):
            self.input_def =  self.workspace.get_input_def(self.step)
        
        # reset input verilog        
        if(self.input_verilog == None):
            self.input_verilog =  self.workspace.get_input_verilog(self.step)
                
        # reset output def
        if(self.output_def == None):
            self.output_def = self.workspace.get_output_def(self.step)
        
        # reset output verilog
        if(self.output_verilog == None):
            self.output_verilog = self.workspace.get_output_verilog(self.step)
        
    def run(self):
        #build flow       
        if(self.eda_tool == EdaTool.IEDA):
            return self.run_ieda()
            
        if(self.eda_tool == EdaTool.INNOVUS):
            return self.run_innovus()
        
        if(self.eda_tool == EdaTool.OPENROAD):
            return self.run_OpenROAD()
        
        if(self.eda_tool == EdaTool.DREAMPLACE):
            return self.run_dreamplace()
        
        if(self.eda_tool == EdaTool.STARRC):
            return self.run_rcx()
        
    def run_feature_ieda(self, reload : bool = False):     
        # save feature        
        feature_io = FeatureIO(dir_workspace = self.dir_workspace,
                               eda_tool = EdaTool.IEDA,
                               feature_option = FeatureOption.summary,
                               flow = self.step)
        
        output_features = feature_io.generate_db_ieda(reload)
        self.result.output_features = output_features
        
        return self.get_result()
        
    def get_result(self):
        self.result.intput_def=self.input_def,
        self.result.input_verilog=self.input_verilog,
        self.result.output_def=self.output_def,
        self.result.output_verilog=self.output_verilog
        
        self.result.print_data()

        return self.result
            
    
    
    