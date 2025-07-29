#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : run_pr_flow.py
@Author : yell
@Desc : run all flow 
'''
import os
from flow.flow_manager import FlowManager
from flow.flow_db import DbFlow
from database.enum import EdaTool, FlowStep
from tools.iEDA.feature.feature import IEDAFeature
from workspace.path import WorkspacePath
from multiprocessing import Process
from engine.floorplan import EngineFloorplan
from engine.cts import EngineCTS
from engine.placement import EnginePlacement
from engine.routing import EngineRouting
from engine.net_opt import EngineNetOpt # input_def = "/data/project_share/dataset/t28/gcd/gcd_floorplan.def"
from engine.timing_opt import EngineTimingOpt
from engine.gds import EngineGDS
from engine.drc import EngineDRC

class RunFlowIEDA:
    '''run eda backend flow
    '''
    
    def __init__(self, dir_workspace : str):        
        self.dir_workspace = dir_workspace
        
        self.workspace = WorkspacePath(dir_workspace)
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
    
    def reset_flow_state(self):
        self.flow_manager.reset_flow_state()

            
    def run_flow(self, flow : DbFlow):
        """run flow"""    
        #set state running
        flow.set_state_running()
        self.flow_manager.save_flow_state(flow)
             
        #run eda tool
        self.run_eda_process(flow)
        
        #save flow state
        if self.check_flow_state(flow) is True:
            flow.set_state_finished()
            self.flow_manager.save_flow_state(flow)
            return True
        else:
            flow.set_state_imcomplete()   
            self.flow_manager.save_flow_state(flow)
            return False 
    
    def run_eda_process(self, flow : DbFlow):   
        """run eda as process"""
        p = Process(target=self.run_eda_tool, args=(self.workspace, flow,))
        p.start()
        p.join()
            
    def run_eda_tool(self, workspace : WorkspacePath, flow : DbFlow):
        io_files = self.build_io_file(flow)
        
        """run eda tool"""  
        if (flow.eda_tool == EdaTool.IEDA):
            # run iEDA
            self.build_flow(flow.step, io_files)
            
            print(io_files)
            
            # # save feature
            # ieda_feature = IEDAFeature(workspace.workspace)
            # ieda_feature.feature_summary(flow, True)
        else:
            pass
    
    def build_io_file(self, flow : DbFlow):
        io_files = {}
        
        io_files["input_def"] = self.workspace.get_input_def(flow)
        io_files["input_verilog"] = self.workspace.get_input_verilog(flow)
            
        io_files["output_def"] = self.workspace.get_output_def(flow=flow, compressed=True)
        io_files["output_verilog"] = self.workspace.get_output_verilog(flow=flow, compressed=True)
        
        return io_files
       
    def build_flow(self, step: FlowStep, io_files : dict):        
        if(step == FlowStep.floorplan):
            ieda_flow = EngineFloorplan(dir_workspace = self.dir_workspace,
                                      input_def = io_files["input_def"],
                                      input_verilog = io_files["input_verilog"],
                                      output_def = io_files["output_def"],
                                      output_verilog = io_files["output_verilog"])
            ieda_flow.run()
        
        if(step == FlowStep.fixFanout):
            ieda_flow = EngineNetOpt(dir_workspace = self.dir_workspace,
                                      input_def = io_files["input_def"],
                                      input_verilog = io_files["input_verilog"],
                                      output_def = io_files["output_def"],
                                      output_verilog = io_files["output_verilog"])
            ieda_flow.run()
            
        if(step == FlowStep.place):
            ieda_flow = EnginePlacement(dir_workspace = self.dir_workspace,
                                      input_def = io_files["input_def"],
                                      input_verilog = io_files["input_verilog"],
                                      output_def = io_files["output_def"],
                                      output_verilog = io_files["output_verilog"])
            ieda_flow.run_placer()
        
        if(step == FlowStep.cts):
            ieda_flow = EngineCTS(dir_workspace = self.dir_workspace,
                                      input_def = io_files["input_def"],
                                      input_verilog = io_files["input_verilog"],
                                      output_def = io_files["output_def"],
                                      output_verilog = io_files["output_verilog"])
            ieda_flow.run()
            
        if(step == FlowStep.optDrv):
            ieda_flow = EngineTimingOpt(dir_workspace = self.dir_workspace,
                                      input_def = io_files["input_def"],
                                      input_verilog = io_files["input_verilog"],
                                      output_def = io_files["output_def"],
                                      output_verilog = io_files["output_verilog"])
            ieda_flow.run_to_drv()
            
        if(step == FlowStep.optHold):
            ieda_flow = EngineTimingOpt(dir_workspace = self.dir_workspace,
                                      input_def = io_files["input_def"],
                                      input_verilog = io_files["input_verilog"],
                                      output_def = io_files["output_def"],
                                      output_verilog = io_files["output_verilog"])
            ieda_flow.run_to_hold()
            
        if(step == FlowStep.optSetup):
            ieda_flow = EngineTimingOpt(dir_workspace = self.dir_workspace,
                                      input_def = io_files["input_def"],
                                      input_verilog = io_files["input_verilog"],
                                      output_def = io_files["output_def"],
                                      output_verilog = io_files["output_verilog"])
            ieda_flow.run_to_setup()
            
        if(step == FlowStep.legalization):
            ieda_flow = EnginePlacement(dir_workspace = self.dir_workspace,
                                      input_def = io_files["input_def"],
                                      input_verilog = io_files["input_verilog"],
                                      output_def = io_files["output_def"],
                                      output_verilog = io_files["output_verilog"])
            ieda_flow.run_legalization()
            
        if(step == FlowStep.route):
            ieda_flow = EngineRouting(dir_workspace = self.dir_workspace,
                                      input_def = io_files["input_def"],
                                      input_verilog = io_files["input_verilog"],
                                      output_def = io_files["output_def"],
                                      output_verilog = io_files["output_verilog"])
            ieda_flow.run_route()
            
        if(step == FlowStep.filler):
            ieda_flow = EnginePlacement(dir_workspace = self.dir_workspace,
                                      input_def = io_files["input_def"],
                                      input_verilog = io_files["input_verilog"],
                                      output_def = io_files["output_def"],
                                      output_verilog = io_files["output_verilog"])
            ieda_flow.run_filler()
            
        if(step == FlowStep.gds):
            ieda_flow = EngineGDS(self.dir_workspace,input_def = io_files["input_def"])
            ieda_flow.run()
        
        if(step == FlowStep.drc):
            ieda_flow = EngineDRC(dir_workspace = self.dir_workspace,
                                      input_def = io_files["input_def"],
                                      input_verilog = io_files["input_verilog"])
            ieda_flow.run()
        
    
    def check_flow_state(self, flow : DbFlow):
        """check state"""
        #check flow success if output def & verilog file exist
        output_def = self.workspace.get_output_def(flow=flow, compressed=True)
        output_verilog = self.workspace.get_output_verilog(flow=flow, compressed=True)
        
        return (os.path.exists(output_def) and os.path.exists(output_verilog))