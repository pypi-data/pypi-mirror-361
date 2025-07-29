#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : cts.py
@Author : yell
@Desc : cts engine api
'''
import os

from engine.base import EngineBase
from flow.flow_db import DbFlow
from database.enum import FlowStep, EdaTool
from tools.iEDA.module.cts import IEDACts
from tools.innovus.module.cts import InnovusCTS
if os.environ.get('OpenROAD') == "on":
    from tools.OpenROAD.module.cts import OpenROADCTS

class EngineCTS(EngineBase):
    """cts engine api"""
    def run(self):
        return super().run()
        
    def run_ieda(self):
        # build flow
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.IEDA,
                              step=FlowStep.place)
        self.step = DbFlow(eda_tool=EdaTool.IEDA,
                      pre_flow=self.pre_step,
                      step=FlowStep.cts)
        self.build_path()
        
        # run iEDA
        run_flow = IEDACts(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog)
        run_flow.run_cts()
        
        return self.run_feature_ieda()
    
    def run_innovus(self):
        # build flow
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.INNOVUS,
                              step=FlowStep.place)
        if(self.step == None):
            self.step = DbFlow(eda_tool=EdaTool.INNOVUS,
                          pre_flow=self.pre_step,
                          step=FlowStep.cts)
            
        self.build_path()
        
        # run innovus
        run_flow = InnovusCTS(dir_workspace = self.dir_workspace,
                               dir_resource = self.dir_resource,
                              input_def = self.input_def, 
                              input_verilog = self.input_verilog,
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog,
                              pre_step = self.pre_step,
                              step = self.step,
                              task = self.task)
        run_flow.run_cts()
        
        # update result
        # self.result.output_features['summary_cts'] = feature_path
        
        return self.get_result()
    
    def run_OpenROAD(self):
        # build flow
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.OPENROAD,
                              step=FlowStep.place)
        if(self.step == None):
            self.step = DbFlow(eda_tool=EdaTool.OPENROAD,
                          pre_flow=self.pre_step,
                          step=FlowStep.cts)
            
        self.build_path()
        
        # run iEDA
        run_flow = OpenROADCTS(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              input_verilog = self.input_verilog,
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog,
                              pre_step = self.pre_step,
                              step = self.step,
                              task = self.task)
        run_flow.run_cts()
        
        return self.get_result()