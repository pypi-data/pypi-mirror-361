#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : full_flow.py
@Author : yell
@Desc : full flow engine api
'''
from engine.base import EngineBase
from flow.flow_db import DbFlow
from database.enum import FlowStep, EdaTool
from tools.innovus.module.full_flow import InnovusFullFlow
from feature.io import FeatureIO

class EngineFullFlow(EngineBase):
    """fullflow engine api"""
    def run(self):
        return super().run()
    
    def run_innovus(self):
        # build flow
        self.step = DbFlow(eda_tool=EdaTool.INNOVUS,
                          step=FlowStep.full_flow)
            
        self.build_path()
        
        # run innovus
        run_flow = InnovusFullFlow(dir_workspace = self.dir_workspace,
                               dir_resource = self.dir_resource,
                              input_def = self.input_def, 
                              input_verilog = self.input_verilog,
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog,
                              step = self.step,
                              task = self.task)
        run_flow.run_full_flow()
        
        # update result
        # self.result.output_features['summary_cts'] = feature_path
        
        return self.get_result()