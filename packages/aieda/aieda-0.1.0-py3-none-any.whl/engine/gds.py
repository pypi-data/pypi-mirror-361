#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : gds.py
@Author : yell
@Desc : gds framework
'''
from engine.base import EngineBase
from database.enum import EdaTool, FlowStep, TaskOption
from flow.flow_db import DbFlow
from tools.iEDA.module.gds import IEDAGds

class EngineGDS(EngineBase):
    """gds framework"""
    def __init__(self, dir_workspace : str, dir_resource : str = "",
                 eda_tool : EdaTool = EdaTool.IEDA, task : TaskOption = TaskOption.RUN_EDA,
                 input_def : str = None, input_verilog : str = None, 
                 output_def : str = None, output_verilog : str = None,
                 pre_step : DbFlow = None, output_gds : str=None):
        super().__init__(dir_workspace, dir_resource,
                 eda_tool, task,
                 input_def, input_verilog, 
                 output_def , output_verilog,
                 pre_step)
        self.output_gds = output_gds
    
    def build_path(self):   
        """rebuild path by flow step"""
        # reset input def
        if(self.input_def == None):
            self.input_def =  self.workspace.get_input_def(self.step)
                
        if(self.output_gds == None):
            self.output_gds = self.workspace.get_output_gds(self.step)
        
    def run(self):
        return super().run()
        
    def run_ieda(self):
        # build flow
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.IEDA,
                              step=FlowStep.filler)
        self.step = DbFlow(eda_tool=EdaTool.IEDA,
                      pre_flow=self.pre_step,
                      step=FlowStep.gds)
        self.build_path()
        
        # run iEDA
        run_flow = IEDAGds(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              output_gds = self.output_gds)
        run_flow.save_gds()
        
        
        self.result.output_gds=self.output_gds
        return self.get_result()
    
    def run_innovus(self):
        pass