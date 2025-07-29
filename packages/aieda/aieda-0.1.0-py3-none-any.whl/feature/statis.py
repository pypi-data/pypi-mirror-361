#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : statis.py
@Author : yell
@Desc : feature statis
'''
from feature.io import FeatureIO
from database.enum import EdaTool, FeatureOption, FlowStep
from workspace.path import WorkspacePath
from flow.flow_db import DbFlow
from database.summary import *
from database.timing import *


class DesignStatis():
    """feature statis"""   
    def __init__(self, dir_workspace : str, eda_tool : EdaTool):
        self.dir_workspace = dir_workspace
        self.eda_tool = eda_tool  
        self.workspace = WorkspacePath(dir_workspace)
        
    def get_statis(self):
        if(self.eda_tool == EdaTool.IEDA):
            return self.get_statis_ieda()
            
        if(self.eda_tool == EdaTool.INNOVUS):
            return self.get_statis_innovus()
        
    def get_statis_ieda(self):
        design_statis = self.get_summary_statis()
        
        return design_statis
    
    def get_statis_innovus(self):
        design_statis = self.get_summary_statis()
        
        return design_statis
                     
    def get_summary_statis(self):
        design_summary = DesignSummary()
             
        # get origin feature summary db
        feature_io = FeatureIO(dir_workspace = self.dir_workspace,
                               eda_tool = self.eda_tool, 
                               feature_option = FeatureOption.summary,
                               flow = DbFlow(eda_tool = self.eda_tool,step = FlowStep.place))
        feature_db = feature_io.get_db()
        
        # common statis
        design_summary.design_name = feature_db.info.design_name
        design_summary.eda_tool = self.eda_tool.value
        design_summary.die_area = feature_db.layout.die_area
        design_summary.core_area = feature_db.layout.core_area
        design_summary.num_iopins = feature_db.statis.num_iopins
        design_summary.num_iopad = feature_db.instances.iopads.num
        design_summary.num_macros = feature_db.instances.macros.num
        design_summary.num_layers = feature_db.layers.num_layers
        design_summary.num_layers_routing = feature_db.layers.num_layers_routing
        design_summary.num_layers_cut = feature_db.layers.num_layers_cut
        design_summary.max_fanout = feature_db.pins.max_fanout
        
        # place
        place_summary = StageSummary()
        place_summary.stage = "place"
        place_summary.die_usage = feature_db.layout.die_usage
        place_summary.core_usage = feature_db.layout.core_usage
        place_summary.num_instances = feature_db.statis.num_instances
        place_summary.num_nets = feature_db.nets.num_total
        place_summary.num_pins = feature_db.nets.num_pins
        place_summary.wire_len = feature_db.nets.wire_len
        
        design_summary.stage_list.append(place_summary)
        
        # CTS
        feature_io = FeatureIO(dir_workspace = self.dir_workspace,
                               eda_tool = self.eda_tool, 
                               feature_option = FeatureOption.summary,
                               flow = DbFlow(eda_tool = self.eda_tool,step = FlowStep.cts))
        feature_db = feature_io.get_db()
        
        cts_summary = StageSummary()
        cts_summary.stage = "CTS"
        cts_summary.die_usage = feature_db.layout.die_usage
        cts_summary.core_usage = feature_db.layout.core_usage
        cts_summary.num_instances = feature_db.statis.num_instances
        cts_summary.num_nets = feature_db.nets.num_total
        cts_summary.num_pins = feature_db.nets.num_pins
        cts_summary.wire_len = feature_db.nets.wire_len
        
        design_summary.stage_list.append(cts_summary)
        
        # route
        feature_io = FeatureIO(dir_workspace = self.dir_workspace,
                               eda_tool = self.eda_tool, 
                               feature_option = FeatureOption.summary,
                               flow = DbFlow(eda_tool = self.eda_tool,step = FlowStep.route))
        feature_db = feature_io.get_db()
        
        route_summary = StageSummary()
        route_summary.stage = "route"
        route_summary.die_usage = feature_db.layout.die_usage
        route_summary.core_usage = feature_db.layout.core_usage
        route_summary.num_instances = feature_db.statis.num_instances
        route_summary.num_nets = feature_db.nets.num_total
        route_summary.num_pins = feature_db.nets.num_pins
        route_summary.wire_len = feature_db.nets.wire_len
        
        design_summary.stage_list.append(route_summary)
        
        return design_summary        