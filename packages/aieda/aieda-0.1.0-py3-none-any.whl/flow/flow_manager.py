#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : flow_manager.py
@Author : yell
@Desc : Manage flow
'''
from dataclasses import field

from workspace.config.json_flow import FlowParser
from database.enum import FlowStep, TaskOption
from flow.flow_db import DbFlow

class FlowManager():
    """Manage flow"""    
    def __init__(self, flow_path : str):
        self.flow_path = flow_path
        self.task : TaskOption = TaskOption.RUN_EDA
        self.flow_list : list = field(default_factory=list)

        self.current_flow = None
        self.pre_flow = None
        self.init_flow()
        
    def get_flow_path(self):
        """get flow path"""
        return self.flow_path
    
    def init_flow(self, flow_path : str=""):
        """set flow path"""
        #save path 
        if(flow_path != ""):            
            self.flow_path = flow_path
        
        #build flow data      
        parser = FlowParser(self.flow_path)
        flow_db_list = parser.get_db()
        if(flow_db_list != None):  
            self.task = flow_db_list['task']
            self.flow_list = flow_db_list['list']
            
    def set_current_flow(self, flow : DbFlow):
        """set current flow"""
        self.current_flow = flow 
        
    def get_current_flow(self):
        """get current flow"""
        return self.current_flow
    
    def set_pre_flow(self, flow : DbFlow):
        """set as pre flow"""
        self.pre_flow = flow
        
    def get_pre_flow(self):
        """get pre flow"""
        return self.pre_flow
    
    def save_flow_state(self, db_flow : DbFlow):
        """save flow state"""
        parser = FlowParser(self.flow_path)
        parser.set_flow_state(db_flow)
    
    def reset_flow_state(self):
        """reset flow state to unstart"""
        parser = FlowParser(self.flow_path)
        parser.reset_flow_state()

    def is_run_eda(self):
        """ if run eda """
        if (self.task == TaskOption.RUN_EDA):
            return True
        else :
            return False
    
    def is_run_fpt(self):
        """run fpt"""
        if (self.task == TaskOption.RUN_FPT):
            return True
        else :
            return False
    
    def set_task(self, task :str):
        """set task"""
        self.task = TaskOption(task)
        
    def get_new_flow(self):
        """get new flow in list"""
        for flow in self.flow_list :
            if flow.is_finish() is not True:
                return flow
            
        return None
    
    def find_flow(self, flow_step : FlowStep):
        for flow in self.flow_list:
            if flow_step == flow.step :
                return flow
