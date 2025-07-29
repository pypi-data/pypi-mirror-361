#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : net_opt.py
@Author : yell
@Desc : net optimization framework
'''
from engine.base import EngineBase
from database.enum import EdaTool, FlowStep
from flow.flow_db import DbFlow
from tools.iEDA.module.net_opt import IEDANetOpt

class EngineNetOpt(EngineBase):
    """net optimization framework"""
    def run(self):
        return super().run()
        
    def run_ieda(self):
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.IEDA,
                              step=FlowStep.floorplan,
                              is_first=True)
        self.step = DbFlow(eda_tool=EdaTool.IEDA,
                        pre_flow=self.pre_step,
                        step=FlowStep.fixFanout)
        self.build_path()
        
        # run iEDA
        run_flow = IEDANetOpt(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog)
        run_flow.run_fix_fanout()
        
        return self.run_feature_ieda()
    
    def run_innovus(self):
        pass