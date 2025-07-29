#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   config_management.py
@Time    :   2024-10-22 20:29:20
@Author  :   SivanLaai
@Version :   1.0
@Contact :   lyhhap@163.com
@Desc    :   
'''
import sys
import os
current_dir = os.path.split(os.path.abspath(__file__))[0]
tool_dir = current_dir.rsplit('/', 2)[0]
sys.path.append(tool_dir)
from enum import Enum
from database.enum import EdaTool, FlowStep 
from flow.flow_db import DbFlow
from workspace.path import WorkspacePath
from flow.flow_manager import FlowManager

from application.DSE.parameter import iEDAParameter, InnovusParameter
import logging

class ConfigManagement:
    def __init__(self, args, eda_tool):
        self.args = args
        self.step = None
        root = self.args.root
        tech = self.args.tech
        design = self.args.project_name
        self.dir_workspace = f"{root}/{tech}/{design}"
        self.workspace = WorkspacePath(self.dir_workspace)
        self.flow_manager = FlowManager(self.workspace.get_config('flow'))

        self.flow_list = list() 
        self.initEdaTool(eda_tool)
        self.initFlowStep()
        self.initConfigPathList()
        self.loadParameters()
        
    def initEdaTool(self, eda_tool):
        if isinstance(eda_tool, Enum):
            self.eda_tool = eda_tool
            return
        if eda_tool == EdaTool.IEDA.value:
            self.eda_tool = EdaTool.IEDA
        elif eda_tool== EdaTool.INNOVUS.value:
            self.eda_tool = EdaTool.INNOVUS
        elif eda_tool==EdaTool.DREAMPLACE.value:
            self.eda_tool = EdaTool.DREAMPLACE
    
    def getEdaTool(self, eda_tool=None):
        if eda_tool is not None:
            if isinstance(eda_tool, Enum):
                return eda_tool
            if eda_tool == EdaTool.IEDA.value:
                eda_tool = EdaTool.IEDA
            elif eda_tool== EdaTool.INNOVUS.value:
                eda_tool = EdaTool.INNOVUS
            elif eda_tool==EdaTool.DREAMPLACE.value:
                eda_tool = EdaTool.DREAMPLACE
            return eda_tool
        return self.eda_tool

    def initFlowList(self):
        if self.step == FlowStep.full_flow:
            tmp_flows = self.args.flows.split(",")
        else:
            tmp_flows = self.args.step.split(",")
        self.flow_manager = FlowManager(self.workspace.get_config('flow'))
        for db_flow in self.flow_manager.flow_list:
            if db_flow.step.value.lower()==tmp_flows[0]:
                self.flow_list.append(DbFlow(eda_tool = self.eda_tool,step = db_flow.step,pre_flow=db_flow.pre_flow))
                break
        for i in range(1, len(tmp_flows)):
            pre_step = self.checkFlowStep(tmp_flows[i-1]) 
            step = self.checkFlowStep(tmp_flows[i]) 
            # print(step)
            self.flow_list.append(DbFlow(eda_tool = self.eda_tool,step = step,pre_flow=self.flow_list[-1]))
        # print(self.flow_list)
        for flow in self.flow_list:
            print(flow.pre_flow.step)
            print(flow.step)
        # exit(0)

    
    def getFlowList(self):
        return self.flow_list
    
    def getFlowStepsByStepArg(self, step_list):
        flow_steps = list()
        for step in step_list:
            flow_steps.append(self.checkFlowStep(step))
        return flow_steps
    
    def checkFlowStep(self, step):
        if step == FlowStep.floorplan.value.lower():
            return FlowStep.floorplan
        
        if step == FlowStep.fixFanout.value.lower():
            return FlowStep.fixFanout
            
        if step == FlowStep.place.value.lower():
            return FlowStep.place
        
        if(step == FlowStep.cts.value.lower()):
            return FlowStep.cts
            
        if step == FlowStep.optDrv.value.lower():
            return FlowStep.optDrv
            
        if step == FlowStep.optHold.value.lower():
            return FlowStep.optHold
            
        if step == FlowStep.optSetup.value.lower():
            return FlowStep.optSetup
            
        if step == FlowStep.legalization.value.lower():
            return FlowStep.legalization
            
        if (step == FlowStep.route.value.lower()):
            return FlowStep.route
            
        if step == FlowStep.filler.value.lower():
            return FlowStep.filler
            
        if step == FlowStep.gds.value.lower():
            return FlowStep.gds
        
        if step == FlowStep.drc.value.lower():
            return FlowStep.drc

    def initFlowStep(self):
        if self.args.step == FlowStep.full_flow.value.lower():
            self.step = FlowStep.full_flow
        elif self.args.step == FlowStep.place.value.lower():
            self.step = FlowStep.place
        elif self.args.step == FlowStep.cts.value.lower():
            self.step = FlowStep.cts
        else:
            pass
        self.initFlowList()
    
    def getConfigPath(self, step):
        config_path = self.workspace.get_config(self.eda_tool.value+"_config").get(step.value, None)
        return config_path

    
    def initConfigPathList(self):
        self.config_paths = dict()
        self.best_config_paths = dict()
        # print("initWorkspace", self.flow_list)
        for db_flow in self.flow_list:
            step = db_flow.step
            step_config_path = self.workspace.get_config(self.eda_tool.value+"_config").get(step.value, None)
            best_step_config_path = self.workspace.get_config(self.eda_tool.value+"_config").get(step.value, None).replace(".json", "_best.json")
            if step_config_path is not None:
                self.config_paths[step.value.lower()] = step_config_path
                self.best_config_paths[step.value.lower()] = best_step_config_path

        if not len(self.config_paths):
            logging.error("self.config_paths is empty, process exit")


    def getConfigPathList(self):
        return self.config_paths
    
    def getBestConfigPathList(self):
        return self.best_config_paths

    def getStep(self):
        return self.step

    def getWorkspacePath(self):
        return  self.dir_workspace

    def loadParameters(self):
        # load parameters
        # self.config_path = self.args.config_path
        # parameter space for iEDA
        eda_tool = self.eda_tool
        if eda_tool==EdaTool.IEDA:
            self.params = iEDAParameter(step=self.step)
            self.params.load_list(self.config_paths)
            # print(self.params.__dict__)
        elif eda_tool==EdaTool.INNOVUS:
            self.params = InnovusParameter()
            self.args.config_path = os.path.join(os.path.dirname(__file__), "config/Innovus/default.json")
            self.config_path = self.args.config_path
            #print(self.config_path)
            self.params.load(self.config_path)
        elif eda_tool==EdaTool.DREAMPLACE:
            pass
    
    def getParameters(self):
        return self.params