
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   parameter.py
@Time    :   2024/08/06 12:44:09
@Author  :   SivanLaai
@Version :   1.0
@Contact :   laaisivan@gmail.com
@Desc    :   parameter space operation for different engines
'''
import sys
import os
# set EDA tools working environment
# option : iEDA innovus PT dreamPlace

current_dir = os.path.split(os.path.abspath(__file__))[0]
tool_dir = current_dir.rsplit('/', 2)[0]
sys.path.append(tool_dir)
from abc import abstractmethod, ABCMeta
import json 
import math 
from collections import OrderedDict
import logging
from database.enum import EdaTool, FlowStep 

class AbstractParameter(metaclass=ABCMeta):
    _search_space = None
    config = {}
    next_params = {}

    '''
    @Func 
    @Desc return
    @Param filename | default parameter json path
           step | step of AiEDA flow
    @Return None
    '''
    def __init__(self, filename="./config/iEDA/default.json", step=FlowStep.place):
        """
        @brief initialization
        """
        filename = os.path.join(os.path.dirname(__file__), filename)
        self._step = step
        self.__dict__ = {}
        # print(step)
        # print(self._step)
        self.initData(filename, step)
        self.formatSearchSpace(step)

    @abstractmethod
    def dumpPlaceFlowConfig(self, filename, config=None, step=FlowStep.place):
        raise NotImplementedError

    @abstractmethod
    def dumpCTSFlowConfig(self, filename, config=None, step=FlowStep.cts):
        raise NotImplementedError

    @abstractmethod
    def dumpRouteFlowConfig(self, filename, config=None, step=FlowStep.route):
        raise NotImplementedError
    
    @abstractmethod
    def dumpFullFlowConfig(self, filename, config=None, flow_list=None):
        raise NotImplementedError

    def dumpConfigByFlowStep(self, filename, flow_step):
        if flow_step == FlowStep.place:
            # self.params_dict[flow_step.value.lower()]
            self.dumpPlaceFlowConfig(filename)
        elif flow_step == FlowStep.cts:
            self.dumpCTSFlowConfig(filename)
        else:
            pass

    @abstractmethod
    def formatSearchSpace(self, step=None):
        raise NotImplementedError

    def getSearchSpace(self, step=None):
        return self._search_space

    @abstractmethod
    def dumpOriginalConfig(self, filename, step=None, flow_list=None):
        raise NotImplementedError
    
    def initData(self, filename, step):
        # print(step)
        params_dict = {}
        with open(filename, "r") as f:
            params_dict = json.load(f, object_pairs_hook=OrderedDict)
        self.__dict__ = dict()
        for param_step in params_dict:
            step_params_dict = params_dict[param_step]
            for key, value in step_params_dict.items():
                if 'default' in value: 
                    if isinstance(value['default'], dict):
                        self.__dict__[key] = dict()
                        for k,v in value['default'].items():
                            self.__dict__[key][k] = v
                    else:
                        self.__dict__[key] = value['default']
                else:
                    self.__dict__[key] = None
        self.__dict__['params_dict'] = params_dict
    
    def getParamsDict(self):
        return self.params_dict
    
    def get(self, key):
        return self.__dict__.get(key, None)

    def set(self, key, value):
        if "." not in key:
            self.__dict__[key] = value
        else:
            key1, key2 = key.split(".")
            if key1 in self.__dict__:
                if isinstance(self.__dict__[key1] ,list):
                    if key2 in self.__dict__[key1][0]:
                        self.__dict__[key1][0][key2] = value
                elif key2 in self.__dict__[key1]:
                    self.__dict__[key1][key2] = value
        if "." not in key:
            self.config[key] = value
        else:
            key1, key2 = key.split(".")
            if key1 in self.config:
                if isinstance(self.config[key1] ,list):
                    if key2 in self.config[key1][0]:
                        self.config[key1][0][key2] = value
                elif key2 in self.config[key1]:
                    self.config[key1][key2] = value

    def toJson(self):
        """
        @brief convert to json
        """
        data = {}
        for key, value in self.__dict__.items():
            if key != 'params_dict': 
                data[key] = value
        return data

    def fromJson(self, data):
        """
        @brief load form json
        """
        for key, value in data.items(): 
            self.__dict__[key] = value


    def dump(self, filename):
        """
        @brief dump to json file
        """
        with open(filename, 'w') as f:
            json.dump(self.toJson(), f)

    def load_list(self, path_list):
        """
        @brief load from json file list
        """
        for step in path_list:
            filepath = path_list[step]
            self.load(filepath, step)
        print(self.config, "load_list")
        self.fromJson(self.config)

    def load(self, filename, step=None):
        """
        @brief load from json file
        """
        with open(filename, 'r') as f:
            data = json.load(f)
            if step is not None:
                self.config[step] = data
            # self.fromJson(self.config[step])

    def updateParams(self, new_param_dict):
        self.next_params = new_param_dict
        print("update self.next_params:", self.next_params)
        # for key,value in new_param_dict.items():
        #     self.config[key] = value


class iEDAParameter(AbstractParameter):

    def __init__(self, filename="./config/iEDA/default.json", step=FlowStep.place):
        self.param_path = os.path.join(os.path.dirname(__file__), filename)
        super().__init__(filename, step)
        # print(self._search_space, "search_space iEDA")

    def formatSearchSpace(self, step):
        search_path = os.path.join(os.path.dirname(__file__), "config/iEDA/search_space.json")
        with open(search_path, "r") as f:
            self.params_dict = json.load(f)
            if step != FlowStep.full_flow:
                self._search_space = self.params_dict.get(step.value.lower(), {})
            else:
                self._search_space = dict()
                for k,v in self.params_dict.items():
                    self._search_space.update(v)
    
    def getCurrUpdateParams(self, step):
        key_step = step.value.lower() # str
        print("next_params:", self.next_params)
        curr_param_keys = self.params_dict.get(key_step, {})
        print("curr_param_keys:", curr_param_keys)
        update_params = { k:v for k,v in self.next_params.items() if k in curr_param_keys }
        print("update_params:", update_params)
        return update_params

    def dumpPlaceFlowConfig(self, filename, config=None, step=FlowStep.place):
        key_step = step.value.lower()
        
        if key_step not in self.config:
            return 
        config = self.config[key_step]
        print("dumpPlaceFlowConfig", config)
        # externals = {key:config[key] for key in config if key != "PL"}
        # logging.info(externals)
        update_params = self.getCurrUpdateParams(step)
        for k in update_params:
            # if k != "PL":
            #     del config[k]
            if k in config["PL"]["GP"]["Wirelength"]:
                config["PL"]["GP"]["Wirelength"][k] = update_params[k]
            if k in config["PL"]["GP"]["Density"]:
                config["PL"]["GP"]["Density"][k] = update_params[k]
            if k in config["PL"]["GP"]["Nesterov"]:
                config["PL"]["GP"]["Nesterov"][k] = update_params[k]
        print("dumpPlaceFlowConfig:", config)
        print("filename:", filename)
        with open(filename, 'w') as f:
            json.dump(config, f, indent=4)

    def dumpCTSFlowConfig(self, filename, config=None, step=FlowStep.cts):
        key_step = step.value.lower()
        if key_step not in self.config:
            return 
        config = self.config[key_step]
        update_params = self.getCurrUpdateParams(step)
        curr_search_space = self.params_dict.get(key_step, {})
        for param in curr_search_space:
            param_type = curr_search_space[param].get("type", None)
            if param_type == "str" and param in update_params:
                config[param] = str(update_params[param])
        with open(filename, 'w') as f:
            json.dump(config, f, indent=4)

    def dumpRouteFlowConfig(self, filename, config=None, step=FlowStep.route):
        pass

    def dumpFullFlowConfig(self, filename, config=None, flow_list=None):
        for flow_step in flow_list:
            self.dumpConfigByFlowStep(filename, flow_step)
        
    def dumpOriginalConfig(self, config_paths=None, flow_list=None, filename=None):
        """
        @brief dump original config parameters to json file
        """
        for flow in flow_list:
            step = flow.step
            filename = config_paths[step.value.lower()]
            print("iEDAParameter: dumpOriginalConfig", step, filename)
            self.dumpConfigByFlowStep(filename, step)

class InnovusParameter(AbstractParameter):

    def __init__(self, filename="./config/Innovus/default.json"):
        super().__init__(filename)

    def formatSearchSpace(self,step):
        search_path = os.path.join(os.path.dirname(__file__), "config/Innovus/search_space.json")
        with open(search_path, "r") as f:
            self._search_space = json.load(f)
    
    def parseParams(self):
        self.args = None
        path = "/home/laixinhua/AiEDA/third_party/resource/innovus/scripts"
        for file_name in os.listdir(path):
            print(file_name)

        
    def dumpOriginalConfig(self, filename, step=None, flow_list=None):
        """
        @brief dump original config parameters to json file
        """
        pass
        

class DREAMPlaceParameter(AbstractParameter):
    def __init__(self, filename="./config/DREAMPlace/params.json"):
        super().__init__(filename)

    def formatSearchSpace(self, step):
        search_path = os.path.join(os.path.dirname(__file__), "config/DREAMPlace/search_space.json")
        with open(search_path, "r") as f:
            self._search_space = json.load(f)

        
    def dumpOriginalConfig(self, filename, step=None, flow_list=None):
        """
        @brief dump original config parameters to json file
        """
        # filter wrong keys
        externals = {key:self.config[key] for key in self.config if key != "PL"}
        logging.info(externals)
        for k in externals:
            # remove wrong keys
            if k != "PL":
                del self.config[k]
        #for k in externals:
            if k in self.config["PL"]["GP"]["Wirelength"]:
                self.config["PL"]["GP"]["Wirelength"][k] = externals[k]
            if k in self.config["PL"]["GP"]["Density"]:
                self.config["PL"]["GP"]["Density"][k] = externals[k]
            if k in self.config["PL"]["GP"]["Nesterov"]:
                self.config["PL"]["GP"]["Nesterov"][k] = externals[k]
        # logging.info(externals)
        #logging.info(externals)
        with open(filename, 'w') as f:
            json.dump(self.config, f, indent=4)

if __name__ == "__main__":
    inn = InnovusParameter()
    inn.parseParams()
    
