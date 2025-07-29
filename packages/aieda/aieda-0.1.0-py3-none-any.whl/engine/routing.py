#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : routing.py
@Author : yell
@Desc : routing framenwork
'''
import os
from engine.base import EngineBase
from database.enum import EdaTool, FlowStep
from flow.flow_db import DbFlow
from tools.iEDA.module.routing import IEDARouting
from tools.innovus.module.routing import InnovusRouting
if os.environ.get('OpenROAD') == "on":
    from tools.OpenROAD.module.routing import OpenROADRouting

class EngineRouting(EngineBase):
    """routing framenwork"""       
    def run(self):
        if(self.step.step == FlowStep.route):
            return self.run_route()
        if(self.step.step == FlowStep.globalRouting):
            return self.run_global_routing()
        if(self.step.step == FlowStep.detailRouting):
            return self.run_detail_routing()

    #######################################################################################    
    # route
    #######################################################################################
    def run_route(self):
        if(self.eda_tool == EdaTool.IEDA):
            return self.run_ieda_route()
        elif(self.eda_tool == EdaTool.INNOVUS):
            return self.run_innovus_route()
        elif(self.eda_tool == EdaTool.OPENROAD):
            if os.environ.get('OpenROAD') == "on":
                return self.run_openroad_route()
            else:
                print("Error, do not support OpenROAD, please install OpenROAD and set OpenROAD environment to 'on'")
                return None
        else:
            print("Error, don't support this tool : " + self.eda_tool.value)
            exit(0)
        
    def run_ieda_route(self):
        # build flow
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.IEDA,
                              step=FlowStep.legalization)
        self.step = DbFlow(eda_tool=EdaTool.IEDA,
                        pre_flow=self.pre_step,
                        step=FlowStep.route)
        self.build_path()
        
        # run iEDA
        run_flow = IEDARouting(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog)
        run_flow.run_routing()
        
        feature_result = self.run_feature_ieda()
        
        run_flow.close_routing()
        
        return feature_result
    
    def run_innovus_route(self):
         # build flow
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.INNOVUS,
                              step=FlowStep.cts)
        if(self.step == None):
            self.step = DbFlow(eda_tool=EdaTool.INNOVUS,
                          pre_flow=self.pre_step,
                          step=FlowStep.route)
            
        self.build_path()
        
        # run innovus
        run_flow = InnovusRouting(dir_workspace = self.dir_workspace,
                               dir_resource = self.dir_resource,
                              input_def = self.input_def, 
                              input_verilog = self.input_verilog,
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog,
                              pre_step = self.pre_step,
                              step = self.step,
                              task = self.task)
        run_flow.run_routing()
        
        # update result
        # self.result.output_features['summary_routing'] = feature_path
        
        return self.get_result()
    
    # route divide into two steps : gr & dr, so the io files need to adjust to the changes
    def run_openroad_route(self):
        # store output 
        if self.output_def == None:
            output_def = self.workspace.get_output_def(self.step)
        else:
            output_def = self.output_def
        if self.output_verilog == None:
            output_verilog = self.workspace.get_output_verilog(self.step)
        else:
            output_verilog = self.output_verilog
        # step 1 run gr
        # reset step
        if(self.step == None):
            print("Please set step")
            exit(0)
            
        self.step.step = FlowStep.globalRouting
        # change output to gr flow
        self.output_def = self.workspace.get_output_def(self.step)
        self.output_verilog = self.workspace.get_output_verilog(self.step)
        
        self.run_openroad_gr()
        # run dr
        # reset prestep & step
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.OPENROAD,
                              step=FlowStep.globalRouting)
        else:
            self.pre_step.step=FlowStep.globalRouting
            
        self.step = DbFlow(eda_tool=EdaTool.OPENROAD,
                          pre_flow=self.pre_step,
                          step=FlowStep.detailRouting)
        # change input to gr 
        self.input_def = self.workspace.get_output_def(self.pre_step)
        self.input_verilog = self.workspace.get_output_verilog(self.pre_step)
        # restore output to origin setting
        self.output_def = output_def
        self.output_verilog = output_verilog
        
        self.run_openroad_dr()
        
        return self.get_result()
    
    #######################################################################################    
    # global routing
    #######################################################################################
    def run_global_routing(self):
        if(self.eda_tool == EdaTool.IEDA):
            return self.run_ieda_gr()
        elif(self.eda_tool == EdaTool.INNOVUS):
            return self.run_innovus_gr()
        elif(self.eda_tool == EdaTool.OPENROAD):
            if os.environ.get('OpenROAD') == "on":
                return self.run_openroad_gr()
            else:
                print("Error, do not support OpenROAD, please install OpenROAD and set OpenROAD environment to 'on'")
                return None
        else:
            print("Error, don't support this tool : " + self.eda_tool.value, + ", step : " + self.step.step.value)
            exit(0)
    
    def run_ieda_gr(self):
        # build flow
        print("Error, don't support this tool : " + self.eda_tool.value, + ", step : " + self.step.step.value)
        pass
    
    def run_innovus_gr(self):
         # build flow
        print("Error, don't support this tool : " + self.eda_tool.value, + ", step : " + self.step.step.value)
        pass
    
    def run_openroad_gr(self):
         # build flow
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.OPENROAD,
                              step=FlowStep.legalization)
        if(self.step == None):
            self.step = DbFlow(eda_tool=EdaTool.OPENROAD,
                          pre_flow=self.pre_step,
                          step=FlowStep.globalRouting)
            
        self.build_path()
        
        # run openroad
        run_flow = OpenROADRouting(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              input_verilog = self.input_verilog,
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog,
                              pre_step = self.pre_step,
                              step = self.step,
                              task = self.task)
        run_flow.run_global_routing()
        
        return self.get_result()
    
#######################################################################################    
    # detail routing
    #######################################################################################
    def run_detail_routing(self):
        if(self.eda_tool == EdaTool.IEDA):
            return self.run_ieda_dr()
        elif(self.eda_tool == EdaTool.INNOVUS):
            return self.run_innovus_dr()
        elif(self.eda_tool == EdaTool.OPENROAD):
            if os.environ.get('OpenROAD') == "on":
                return self.run_openroad_dr()
            else:
                print("Error, do not support OpenROAD, please install OpenROAD and set OpenROAD environment to 'on'")
                return None
        else:
            print("Error, don't support this tool : " + self.eda_tool.value, + ", step : " + self.step.step.value)
            exit(0)
    
    def run_ieda_dr(self):
        # build flow
        print("Error, don't support this tool : " + self.eda_tool.value, + ", step : " + self.step.step.value)
        pass
    
    def run_innovus_dr(self):
         # build flow
        print("Error, don't support this tool : " + self.eda_tool.value, + ", step : " + self.step.step.value)
        pass
    
    def run_openroad_dr(self):
         # build flow
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.OPENROAD,
                              step=FlowStep.globalRouting)
        if(self.step == None):
            self.step = DbFlow(eda_tool=EdaTool.OPENROAD,
                          pre_flow=self.pre_step,
                          step=FlowStep.detailRouting)
            
        self.build_path()
        
        # run openroad
        run_flow = OpenROADRouting(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              input_verilog = self.input_verilog,
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog,
                              pre_step = self.pre_step,
                              step = self.step,
                              task = self.task)
        run_flow.run_detail_routing()
        
        return self.get_result()