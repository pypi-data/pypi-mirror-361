#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : drc.py
@Author : yell
@Desc : drc framework
'''
from engine.base import EngineBase
from flow.flow_db import DbFlow
from database.enum import FlowStep, EdaTool
from tools.iEDA.module.drc import IEDADrc
from tools.iEDA.feature.feature import IEDAFeature
from tools.innovus.module.drc import InnovusDRC

class EngineDRC(EngineBase):
    """drc framework"""
    def run(self):
        return super().run()
        
    def run_ieda(self):
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.IEDA,
                            step=FlowStep.route)
        self.step = DbFlow(eda_tool=EdaTool.IEDA,
                      pre_flow=self.pre_step,
                      step=FlowStep.drc)
        self.build_path()
        
        # run iEDA drc
        run_flow = IEDADrc(dir_workspace = self.dir_workspace,
                              input_def = self.input_def)
        run_flow.run_drc()
        
        return None
    
    def run_innovus(self):
        # build flow
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.INNOVUS,
                              step=FlowStep.route)
        if(self.step == None):
            self.step = DbFlow(eda_tool=EdaTool.INNOVUS,
                          pre_flow=self.pre_step,
                          step=FlowStep.drc)
            
        self.build_path()
        
        # run innovus
        run_flow = InnovusDRC(dir_workspace = self.dir_workspace,
                               dir_resource = self.dir_resource,
                              input_def = self.input_def, 
                              input_verilog = self.input_verilog,
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog,
                              pre_step = self.pre_step,
                              step = self.step,
                              task = self.task)
        run_flow.run_drc()
        
        return self.get_result()