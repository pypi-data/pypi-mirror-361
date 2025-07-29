#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : placement.py
@Author : yell
@Desc : placement framework
'''
import os

from engine.base import EngineBase
from database.enum import EdaTool, FlowStep
from flow.flow_db import DbFlow
from tools.iEDA.module.placement import IEDAPlacement
from tools.innovus.module.placement import InnovusPlacement

if os.environ.get('DREAMPlace') == "on":
    from tools.DREAMPlace.run_dreamplace import DreamPlace
if os.environ.get('Xplace') == "on":
    from tools.Xplace.run_xplace import RunXPlace
if os.environ.get('OpenROAD') == "on":
    from tools.OpenROAD.module.placement import OpenROADPlacement

class EnginePlacement(EngineBase):
    """placement framework"""
    def run(self):
        if(self.step.step == FlowStep.prePlace):
            return self.run_pre_placer()
        if(self.step.step == FlowStep.place):
            return self.run_placer()
        if(self.step.step == FlowStep.globalPlace):
            return self.run_global_placement()
        if(self.step.step == FlowStep.detailPlace):
            return self.run_detail_placement()
        if(self.step.step == FlowStep.legalization):
            return self.run_legalization()
        if(self.step.step == FlowStep.filler):
            return self.run_filler()

    #######################################################################################    
    # placement
    #######################################################################################
    def run_pre_placer(self):
        if(self.eda_tool == EdaTool.INNOVUS):
            return self.run_pre_placer_innovus()
        else:
            print("only supper innovus pre place.")
            exit(0)
        
    
    def run_pre_placer_innovus(self):
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.INNOVUS,
                              step=FlowStep.floorplan)
        if(self.step == None):
            self.step = DbFlow(eda_tool=EdaTool.INNOVUS,
                          pre_flow=self.pre_step,
                          step=FlowStep.prePlace)
            
        self.build_path()
        
        # run iEDA
        run_flow = InnovusPlacement(dir_workspace = self.dir_workspace,
                               dir_resource = self.dir_resource,
                              input_def = self.input_def, 
                              input_verilog = self.input_verilog,
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog,
                              pre_step = self.pre_step,
                              step = self.step,
                              task = self.task)
        run_flow.run_pre_place()
        
        # update result
        # self.result.output_features['summary_preplace'] = feature_path
        
        return self.get_result()

    #######################################################################################    
    # placement
    #######################################################################################
    def run_placer(self):
        if(self.eda_tool == EdaTool.IEDA):
            return self.run_placer_ieda()
            
        if(self.eda_tool == EdaTool.INNOVUS):
            return self.run_placer_innovus()
        
        if(self.eda_tool == EdaTool.DREAMPLACE):
            if os.environ.get('DREAMPlace') == "on":
                return self.run_placer_dreamplace()
            else:
                print("Error, do not support DREAMPlace, please install DREAMPlace and set DREAMPlace environment to 'on'")
                return None
        
        if(self.eda_tool == EdaTool.XPLACE):
            if os.environ.get('Xplace') == "on":
                return self.run_placer_xplace()
            else:
                print("Error, do not support XPlace, please install XPlace and set Xplace environment to 'on'")
                return None
        
    def run_placer_ieda(self):
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.IEDA,
                              step=FlowStep.fixFanout)
        self.step = DbFlow(eda_tool=EdaTool.IEDA,
                        pre_flow=self.pre_step,
                        step=FlowStep.place)
        self.build_path()
        
        # run iEDA
        run_flow = IEDAPlacement(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog)
        run_flow.run_placement()
        
        return self.run_feature_ieda()
    
    def run_placer_innovus(self):
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.INNOVUS,
                              step=FlowStep.prePlace)
        if(self.step == None):
            self.step = DbFlow(eda_tool=EdaTool.INNOVUS,
                          pre_flow=self.pre_step,
                          step=FlowStep.place)
            
        self.build_path()
        
        # run innovus
        run_flow = InnovusPlacement(dir_workspace = self.dir_workspace,
                               dir_resource = self.dir_resource,
                              input_def = self.input_def, 
                              input_verilog = self.input_verilog,
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog,
                              pre_step = self.pre_step,
                              step = self.step,
                              task = self.task)
        run_flow.run_place()
        
        # update result
        # self.result.output_features['summary_placement'] = feature_path
        
        return self.get_result()
    
    def run_placer_dreamplace(self):
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.IEDA,
                              step=FlowStep.fixFanout)
        self.step = DbFlow(eda_tool=EdaTool.DREAMPLACE,
                        pre_flow=self.pre_step,
                        step=FlowStep.place)
        self.build_path()
        
        # run DREAMPlace
        run_flow = DreamPlace(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              input_verilog= self.input_verilog, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog)
        run_flow.run_placement()
        
        return self.run_feature_ieda(True)
    
    def run_placer_xplace(self):
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.IEDA,
                              step=FlowStep.fixFanout)
        self.step = DbFlow(eda_tool=EdaTool.XPLACE,
                        pre_flow=self.pre_step,
                        step=FlowStep.place)
        self.build_path()
        
        # run xplace
        run_flow = RunXPlace(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              input_verilog= self.input_verilog, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog)
        run_flow.run_placement()
        
        return self.run_feature_ieda(True)
    
    #######################################################################################    
    # global placement
    #######################################################################################
    def run_global_placement(self):  
        if(self.eda_tool == EdaTool.OPENROAD):
            if os.environ.get('OpenROAD') == "on":
                return self.run_gp_OpenROAD()
            else:
                print("Error, do not support OpenROAD, please install OpenROAD and set OpenROAD environment to 'on'")
                return None
        else:
            print("Error, don't support global placemenet for tool " + self.eda_tool.value)
        
        
    def run_gp_OpenROAD(self):
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.OPENROAD,
                              step=FlowStep.fixFanout)
        if(self.step == None):
            self.step = DbFlow(eda_tool=EdaTool.OPENROAD,
                        pre_flow=self.pre_step,
                        step=FlowStep.globalPlace)
        self.build_path()
        
        # run
        run_flow = OpenROADPlacement(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog,
                              pre_step = self.pre_step,
                              step = self.step)
        run_flow.run_global_placement()
        
        return self.run_feature_ieda(reload=True)
    
    #######################################################################################    
    # detail placement
    #######################################################################################
    def run_detail_placement(self):  
        if(self.eda_tool == EdaTool.OPENROAD):
            if os.environ.get('OpenROAD') == "on":
                return self.run_dp_OpenROAD()
            else:
                print("Error, do not support OpenROAD, please install OpenROAD and set OpenROAD environment to 'on'")
                return None
        else:
            print("Error, don't support detail placemenet for tool " + self.eda_tool.value)
        
        
    def run_dp_OpenROAD(self):
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.OPENROAD,
                              step=FlowStep.globalPlace)
        if(self.step == None):
            self.step = DbFlow(eda_tool=EdaTool.OPENROAD,
                        pre_flow=self.pre_step,
                        step=FlowStep.detailPlace)
        self.build_path()
        
        # run openroad
        run_flow = OpenROADPlacement(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog,
                              pre_step = self.pre_step,
                              step = self.step)
        run_flow.run_detail_placement()
        
        return self.run_feature_ieda(reload=True)
    
    #######################################################################################    
    # legalization
    #######################################################################################  
    def run_legalization(self):
        if(self.eda_tool == EdaTool.IEDA):
            return self.run_legalization_ieda()
            
        if(self.eda_tool == EdaTool.INNOVUS):
            return self.run_legalization_innovus()
        
        if(self.eda_tool == EdaTool.DREAMPLACE):
            return self.run_legalization_dreamplace()
        
    def run_legalization_ieda(self):
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.IEDA,
                              step=FlowStep.optHold)
        self.step = DbFlow(eda_tool=EdaTool.IEDA,
                        pre_flow=self.pre_step,
                        step=FlowStep.legalization)
        self.build_path()
        
        # run iEDA
        run_flow = IEDAPlacement(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog)
        run_flow.run_legalization()
        
        return self.run_feature_ieda()
    
    def run_legalization_innovus(self):
        pass
    
    def run_legalization_dreamplace(self):
        return None
    
    #######################################################################################    
    # filler
    #######################################################################################
    def run_filler(self):
        if(self.eda_tool == EdaTool.IEDA):
            return self.run_filler_ieda()
            
        if(self.eda_tool == EdaTool.INNOVUS):
            return self.run_filler_innovus()
        
        if(self.eda_tool == EdaTool.DREAMPLACE):
            return self.run_filler_dreamplace()
        
    def run_filler_ieda(self):
        if(self.pre_step == None):
            self.pre_step = DbFlow(eda_tool=EdaTool.IEDA,
                            step=FlowStep.route)
        self.step = DbFlow(eda_tool=EdaTool.IEDA,
                      pre_flow=self.pre_step,
                      step=FlowStep.filler)
        self.build_path()
        
        # run iEDA
        run_flow = IEDAPlacement(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog)
        run_flow.run_filler()
        
        return self.run_feature_ieda()
    
    def run_filler_innovus(self):
        pass
    
    def run_filler_dreamplace(self):
        pass