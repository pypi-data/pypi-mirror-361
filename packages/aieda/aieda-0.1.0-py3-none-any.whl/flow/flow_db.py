#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : flow_manager.py
@Author : yell
@Desc : Manage flow
'''
from dataclasses import dataclass

from database.enum import FlowStep, EdaTool, PTState, TaskState, FptState

@dataclass
class DbFlow(object):
    """flow data structure"""
    eda_tool : EdaTool  = None
    pre_flow : any = None
    step : FlowStep = FlowStep.NoStep
    state : TaskState = TaskState.Unstart
    fpt_state : FptState = FptState.on
    pt_state : PTState = PTState.off
    is_first : bool = False

    def set_state_unstart(self):
        """set_state_unstart"""
        self.state = TaskState.Unstart
    
    def set_state_running(self):
        """set_state_running"""
        self.state = TaskState.Ongoing
        
    def set_state_finished(self):
        """set_state_finished"""
        self.state = TaskState.Success
    
    def set_state_imcomplete(self):
        """set_state_imcomplete"""
        self.state = TaskState.Imcomplete
        
    def set_first_flow(self):
        """set_first_flow"""
        self.is_first = True
        
    def is_new(self):
        """get task new"""
        if( self.state != TaskState.Unstart):
            return True
        else :
            return False
        
    def is_ongoing(self):
        """if task is ongoing"""
        if( self.state == TaskState.Ongoing):
            return True
        else :
            return False
    
    def is_finish(self):
        """if task finished"""
        if( self.state == TaskState.Success):
            return True
        else :
            return False
        
    def is_imcomplete(self):
        """is task not finished"""
        if( self.state == TaskState.Imcomplete):
            return True
        else :
            return False
        
    def is_first_flow(self):
        """if 1st flow in flowlist"""
        return self.is_first
    
    def has_fpt(self):
        """do fpt"""
        if( self.fpt_state == FptState.on):
            return True
        else :
            return False
    
    def has_pt(self):
        """do pt"""
        if( self.pt_state == PTState.on):
            return True
        else :
            return False