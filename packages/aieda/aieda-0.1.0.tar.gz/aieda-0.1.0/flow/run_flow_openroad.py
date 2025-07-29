#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : run_pr_flow.py
@Author : yell
@Desc : run all flow 
'''
import os

from flow.flow_db import DbFlow
from database.enum import EdaTool, FlowStep
from workspace.path import WorkspacePath
from flow.flow_manager import FlowManager
from tools.fpt.api.tech_api import TechDRCsApi
from engine.floorplan import EngineFloorplan
from engine.cts import EngineCTS
from engine.placement import EnginePlacement
from engine.routing import EngineRouting
from engine.drc import EngineDRC
from engine.full_flow import EngineFullFlow

class RunFlowOpenROAD:
    '''run eda backend flow
    '''
    
    def __init__(self, dir_workspace : str, dir_resource : str=""):
        self.dir_workspace = dir_workspace
        self.dir_resource = dir_resource
        
        self.workspace = WorkspacePath(dir_workspace, dir_resource)
        self.flow_manager = FlowManager(self.workspace.get_config('flow'))
    
    def run(self):
        """run flow"""  
        flow = self.flow_manager.get_new_flow()
        while flow is not None :
            #run flow 
            self.flow_manager.set_current_flow(flow)
            if self.run_flow(flow) is False:
                return False
            #set as pre flow
            self.flow_manager.set_pre_flow(flow)
            #get next flow
            flow = self.flow_manager.get_new_flow()
          
        #check all flow success  
        for check_flow in self.flow_manager.flow_list :
            if check_flow.is_finish() is False:
                return False
        
        return True
            
    def run_flow(self, flow : DbFlow):
        """run flow"""    
        #set state running
        flow.set_state_running()
        self.flow_manager.save_flow_state(flow)
            
        #run eda tool
        self.run_eda_tool(flow)
        
        #save flow state
        if self.check_flow_state(flow) is True:
            flow.set_state_finished()
            self.flow_manager.save_flow_state(flow)
            return True
        else:
            flow.set_state_imcomplete()   
            self.flow_manager.save_flow_state(flow)
            return False 
            
    def run_eda_tool(self,  flow : DbFlow):
        io_files = self.build_io_file(flow)

        """run eda tool"""
        
        if (flow.eda_tool == EdaTool.INNOVUS):
            # run innovus
            self.build_flow(flow.step, io_files)

            print(io_files)
        else:
            pass

    def build_io_file(self, flow : DbFlow):
        io_files = {}
        
        io_files["input_def"] = self.workspace.get_input_def(flow)
        io_files["input_verilog"] = self.workspace.get_input_verilog(flow)
            
        io_files["output_def"] = self.workspace.get_output_def(flow)
        io_files["output_verilog"] = self.workspace.get_output_verilog(flow)
        
        return io_files        
    
    def check_flow_state(self, flow : DbFlow):
        """check state"""
        #check flow success if output def & verilog file exist
        output_def = self.workspace.get_output_def(flow)
        output_verilog = self.workspace.get_output_verilog(flow)
        
        return (os.path.exists(output_def) and os.path.exists(output_verilog))
        
   
    def build_flow(self, step: FlowStep, io_files : dict):
        print("Current Step:", step)
        if(step == FlowStep.floorplan):
            run_flow = EngineFloorplan(dir_workspace = self.dir_workspace,
                                      eda_tool = EdaTool.OPENROAD,
                                      input_def = io_files["input_def"],
                                      input_verilog = io_files["input_verilog"],
                                      output_def = io_files["output_def"],
                                      output_verilog = io_files["output_verilog"])
            run_flow.run()
        
        if(step == FlowStep.prePlace):
            run_flow = EnginePlacement(dir_workspace = self.dir_workspace,
                                      eda_tool = EdaTool.OPENROAD,
                                      input_def = io_files["input_def"],
                                      input_verilog = io_files["input_verilog"],
                                      output_def = io_files["output_def"],
                                      output_verilog = io_files["output_verilog"])
            run_flow.run_pre_placer()
            
        if(step == FlowStep.place):
            run_flow = EnginePlacement(dir_workspace = self.dir_workspace,
                                      eda_tool = EdaTool.OPENROAD,
                                      input_def = io_files["input_def"],
                                      input_verilog = io_files["input_verilog"],
                                      output_def = io_files["output_def"],
                                      output_verilog = io_files["output_verilog"])
            run_flow.run_placer()
        
        if(step == FlowStep.cts):
            run_flow = EngineCTS(dir_workspace = self.dir_workspace,
                                      eda_tool = EdaTool.OPENROAD,
                                      input_def = io_files["input_def"],
                                      input_verilog = io_files["input_verilog"],
                                      output_def = io_files["output_def"],
                                      output_verilog = io_files["output_verilog"])
            run_flow.run()
            
        if(step == FlowStep.route):
            run_flow = EngineRouting(dir_workspace = self.dir_workspace,
                                      eda_tool = EdaTool.OPENROAD,
                                      input_def = io_files["input_def"],
                                      input_verilog = io_files["input_verilog"],
                                      output_def = io_files["output_def"],
                                      output_verilog = io_files["output_verilog"])
            run_flow.run()