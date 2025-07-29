#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : base.py
@Author : yell
@Desc : feature io 
'''
from feature.base import FeatureBase
from tools.iEDA.utility.base import IEDABase
from database.enum import EdaTool, FeatureOption, FlowStep
from workspace.path import WorkspacePath
from multiprocessing import Process
from flow.flow_db import DbFlow
from utility.json_parser import JsonParser
import json

from tools.iEDA.feature.feature import IEDAFeature
from tools.innovus.feature.feature import InnovusFeature

class FeatureIO(FeatureBase):
    """feature base"""                
    def generate_db_ieda(self, reload : bool = False):        
        # if reload = True, read def again by process
        if(reload == True):
            p = Process(target=self.generate_db_ieda_process, args=(self.workspace, 
                                                                    self.flow,
                                                                    reload,
                                                                    self.input_def))
            p.start()
            p.join()
            
            return None
        else:
            ieda_feature = IEDAFeature(self.dir_workspace)
            # get feature
            path_summary = ieda_feature.feature_summary(flow = self.flow)
            if(reload == False):
                path_tool = ieda_feature.feature_tool(flow = self.flow)
            
            # design_eval_path = ieda_feature.feature_eval_summary(flow = self.flow)
            # net_eval_path = ieda_feature.feature_net_eval(flow = self.flow)
            
            output_features = {}
            output_features['summary'] = path_summary
            if(reload == False):
                output_features['tools'] = path_tool
            
            # output_features['design_eval_path'] = design_eval_path
            # output_features['net_eval_path'] = net_eval_path
            
            return output_features
    
    def generate_db_ieda_process(self, workspace_path : WorkspacePath, 
                                 flow : DbFlow,
                                 reload : bool = False,
                                 input_def : str = ""):        
        ieda_feature = IEDAFeature(workspace_path.workspace)
        # if reload = True, read def again
        if(reload == True):
            if(input_def == None):
                input_def = workspace_path.get_output_def(flow)
                # input_def = workspace_path.get_output_def(flow, False)
            ieda_feature.read_def(input_def)
            
        # get feature
        path_summary = ieda_feature.feature_summary(flow = flow)
        
        if (flow.step == DbFlow.step.place):
            design_eval_path, net_eval_path = ieda_feature.feature_pl_eval_union(flow = flow)
            print("eval_path = ", design_eval_path)
            print("net_eval_path = ", net_eval_path)    
        elif (flow.step == DbFlow.step.cts):
            design_eval_path, net_eval_path = ieda_feature.feature_cts_eval_union(flow = flow)
            print("eval_path = ", design_eval_path)
            print("net_eval_path = ", net_eval_path)    

        print("summary_path = ", path_summary)

        if(reload == False):
            path_tool = ieda_feature.feature_tool(flow = flow)
            print("path_tool = ", path_tool)
           
    def get_raw_json(self, feature_option : FeatureOption = FeatureOption.NoFeature):
        try:
            if(feature_option != FeatureOption.NoFeature):
                self.feature_option = feature_option

            reader = IEDABase(self.dir_workspace)      
            raw_json_path = reader.workspace.get_feature_jsonl(self.flow, feature_option=self.feature_option)
            data = dict()
            with open(raw_json_path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    line_data = json.loads(line.strip())
                    data.update(line_data)
        except Exception as e:
            pass
        finally:
            return data
    
    def gernerate_db_ieda_by_innovus(self):
        # place
        feature_innovus = InnovusFeature(self.dir_workspace)
        feature_innovus.feature_timing(flow=self.flow, feature_option=FeatureOption.baseline_sta)
        feature_innovus.feature_power(flow=self.flow, feature_option=FeatureOption.baseline_power)
    
    def get_db_ieda(self):
        if(self.flow == None):
            print("Error : flow must be set to get db.")
            return
        
        if(self.feature_option == FeatureOption.summary):
            reader = IEDAFeature(self.dir_workspace)      
            summary = reader.feature_db_summary(self.flow)
            
            return summary
        
        if(self.feature_option == FeatureOption.tools):
            reader = IEDAFeature(self.dir_workspace)      
            tool_feature = reader.feature_db_tools(self.flow)
            
            return tool_feature

        if(self.feature_option == FeatureOption.eval):
            reader = IEDAFeature(self.dir_workspace)      
            eval_feature = reader.feature_db_eval(self.flow)
            
            return eval_feature
        
        if(self.feature_option == FeatureOption.baseline_sta):
            reader = InnovusFeature(self.dir_workspace)     
            sta_feature = reader.feature_db_timing(flow=self.flow, feature_option=FeatureOption.baseline_sta)
            
            return sta_feature
        
        if(self.feature_option == FeatureOption.baseline_power):
            reader = InnovusFeature(self.dir_workspace)     
            power_feature = reader.feature_db_power(flow=self.flow, feature_option=FeatureOption.baseline_power)
            
            return power_feature
        
    def generate_db_innovus(self):
        feature = InnovusFeature(self.dir_workspace)
        
        # feature tools by innovus feature
        feature.feature_tools()
        
        # feature summary by iEDA
        self.generate_db_ieda(reload=True)
    
    def get_db_innovus(self):
        if(self.flow == None):
            print("Error : flow must be set to get db.")
            return
        
        if(self.feature_option == FeatureOption.summary):
            reader = InnovusFeature(self.dir_workspace)      
            summary = reader.feature_db_summary(self.flow)
            
            return summary
        
        if(self.feature_option == FeatureOption.tools):
            reader = InnovusFeature(self.dir_workspace)      
            tool_feature = reader.feature_db_tools(self.flow)
            
            return tool_feature
        
    def gernerate_route_data(self, json_path : str, reload : bool = False):
        if(reload == True):
            p = Process(target=self.gernerate_route_data_process, args=(self.workspace, 
                                                                    json_path,
                                                                    self.flow,
                                                                    reload,
                                                                    self.input_def))
            p.start()
            p.join()
        else:
            ieda_feature = IEDAFeature(self.dir_workspace)
            # read json 
            ieda_feature.feature_route_read(json_path)
            
            # save route data to json
            ieda_feature.feature_route(json_path)
    
    # run as process
    def gernerate_route_data_process(self, workspace_path : WorkspacePath, 
                                 json_path : str,
                                 flow : DbFlow,
                                 reload : bool = False,
                                 input_def : str = ""):   
        # route data            
        ieda_feature = IEDAFeature(workspace_path.workspace)
        # if reload = True, read def again
        if(reload == True):
            if(input_def == None):
                input_def = workspace_path.get_output_def(flow)
            ieda_feature.read_def(input_def)
            
        # read json 
        ieda_feature.feature_route_read(json_path)
        
        # save route data to json
        ieda_feature.feature_route(json_path)

    def generate_eval_ieda(self):        
        ieda_feature = IEDAFeature(self.dir_workspace)
        eval_path = ieda_feature.feature_eval_summary(flow = self.flow)
        return eval_path
    
    def generate_timing_eval_ieda(self):        
        ieda_feature = IEDAFeature(self.dir_workspace)
        eval_path = ieda_feature.feature_timing_eval_summary(flow = self.flow)
        return eval_path
    
    def generate_net_eval_ieda(self):
        ieda_feature = IEDAFeature(self.dir_workspace)
        eval_path = ieda_feature.feature_net_eval(flow = self.flow)
        return eval_path
    
        