#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : timing_opt.py
@Author : yell
@Desc : timing optimization framework
'''
from engine.base import EngineBase
from database.enum import EdaTool, FlowStep
from flow.flow_db import DbFlow
from tools.iEDA.module.timing_opt import IEDATimingOpt

class EngineTimingOpt(EngineBase):
    """timing optimization framework"""   
    
    #######################################################################################    
    # timing optimization for drv
    #######################################################################################
    def run_to_drv(self):
        if(self.eda_tool == EdaTool.IEDA):
            return self.run_to_drv_ieda()
            
        if(self.eda_tool == EdaTool.INNOVUS):
            return self.run_to_drv_innovus()
        
        
    def run_to_drv_ieda(self):
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.IEDA,
                            step=FlowStep.cts)
        self.step = DbFlow(eda_tool=EdaTool.IEDA,
                        pre_flow=self.pre_step,
                        step=FlowStep.optDrv)
        self.build_path()
        
        # run iEDA
        run_flow = IEDATimingOpt(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog)
        run_flow.run_to_drv()
        
        return self.run_feature_ieda()
    
    def run_to_drv_innovus(self):
        pass
    
    #######################################################################################    
    # timing optimization for hold
    #######################################################################################  
    def run_to_hold(self):
        if(self.eda_tool == EdaTool.IEDA):
            return self.run_to_hold_ieda()
            
        if(self.eda_tool == EdaTool.INNOVUS):
            return self.run_to_hold_innovus()
        
    def run_to_hold_ieda(self):
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.IEDA,
                            step=FlowStep.optDrv)
        self.step = DbFlow(eda_tool=EdaTool.IEDA,
                      pre_flow=self.pre_step,
                      step=FlowStep.optHold)
        self.build_path()
        
        # run iEDA
        run_flow = IEDATimingOpt(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog)
        run_flow.run_to_hold()
        
        return self.run_feature_ieda()
    
    def run_to_hold_innovus(self):
        pass
    
    #######################################################################################    
    # timing optimization for setup
    #######################################################################################  
    def run_to_setup(self):
        if(self.eda_tool == EdaTool.IEDA):
            return self.run_to_setup_ieda()
            
        if(self.eda_tool == EdaTool.INNOVUS):
            return self.run_to_setup_innovus()
        
    def run_to_setup_ieda(self):
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.IEDA,
                              step=FlowStep.optHold)
        self.step = DbFlow(eda_tool=EdaTool.IEDA,
                      pre_flow=self.pre_step,
                      step=FlowStep.optSetup)
        self.build_path()
        
        # run iEDA
        run_flow = IEDATimingOpt(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog)
        run_flow.run_to_setup()
        
        return self.run_feature_ieda()
    
    def run_to_setup_innovus(self):
        pass
    