#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : rcx.py
@Author : yexinyu
@Desc : RCX framenwork
'''

import sys 
sys.path.insert(0, r'/home/yexinyu/AiEDA')
sys.path.insert(0, r'/home/yexinyu/AiEDA/database/enum.py')
import os
from engine.base import EngineBase
from database.enum import EdaTool, FlowStep
# if os.environ.get('StarRC') == "on":
from tools.StarRC.module.rcx import StarRCRcx 

class EngineRCX(EngineBase):
    """routing framenwork"""   
    def __init__(self, dir_workspace, dir_resource = "", eda_tool = EdaTool.STARRC, input_def = "", block = "" , output_spef=None
                #  step = FlowStep.rcx
                 ):
        super().__init__(dir_workspace, dir_resource, eda_tool, input_def, block, output_spef)

    def run(self):
        if(self.step == FlowStep.rcx):
            return self.run_rcx()

    #######################################################################################    
    # rcx
    #######################################################################################
    def run_rcx(self, input_def, block): 
        if(self.eda_tool == EdaTool.STARRC):
            return self.run_starrc_rcx(input_def, block)
        # elif(self.eda_tool == EdaTool.INNOVUS):
        #     return self.run_innovus_rcx()
        else:
            print("Error, don't support this tool : " + self.eda_tool.value)
            exit(0)
        

    def run_starrc_rcx(self,input_def, block):
            
        # self.build_path()
        
        # run StarRC
        run_flow = StarRCRcx(dir_workspace = self.dir_workspace,
                            dir_resource = self.dir_resource,
                            input_def = input_def, 
                            input_verilog = self.input_verilog,
                            output_spef = self.output_spef, 
                            output_verilog = self.output_verilog,
                            pre_step = self.pre_step,
                            step = self.step,
                            task = self.task)
    
   
        run_flow.run_rcx(input_def, block)
        return self.get_result()
    
