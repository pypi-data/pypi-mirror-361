#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : floorplan.py
@Author : yell
@Desc : floorplan framework
'''
import os

from engine.base import EngineBase
from database.enum import EdaTool, FlowStep
from flow.flow_db import DbFlow
from tools.iEDA.module.floorplan import IEDAFloorplan
from tools.innovus.module.floorplan import InnovusFloorplan

if os.environ.get('OpenROAD') == "on":
    from tools.OpenROAD.module.floorplan import OpenROADFloorplan

class EngineFloorplan(EngineBase):
    """floorplan framework"""
    def run(self):
        return super().run()
        
    
    def run_ieda(self):
        # build flow
        self.step = DbFlow(eda_tool=EdaTool.IEDA,
                      step=FlowStep.floorplan)
        self.build_path()
        
        # run iEDA
        run_flow = IEDAFloorplan(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog)
        run_flow.run_floorplan()
        
        return self.run_feature_ieda()
    
    def run_innovus(self):
        # build flow
        self.step = DbFlow(eda_tool=EdaTool.INNOVUS,
                      step=FlowStep.floorplan)
        self.build_path()
        
        # run
        run_flow = InnovusFloorplan(dir_workspace = self.dir_workspace,
                               dir_resource = self.dir_resource,
                              input_def = self.input_def, 
                              input_verilog = self.input_verilog,
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog,
                              step = self.step,
                              task = self.task)
        run_flow.run_floorplan()
        
        # update result
        return self.get_result()
    
    def run_OpenROAD(self):
        # build flow
        self.step = DbFlow(eda_tool=EdaTool.OPENROAD,
                      step=FlowStep.floorplan)
        self.build_path()
        
        # run
        run_flow = OpenROADFloorplan(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              input_verilog = self.input_verilog,
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog,
                              step = self.step,
                              task = self.task)
        run_flow.run_floorplan()
        
        # update result
        return self.get_result()