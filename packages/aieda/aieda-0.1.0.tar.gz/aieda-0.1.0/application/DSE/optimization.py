#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   optimization.py
@Time    :   2024/08/06 12:44:09
@Author  :   SivanLaai
@Version :   1.0
@Contact :   laaisivan@gmail.com
@Desc    :   different optimization method
'''
import sys
import os
from multiprocessing import  Process
# set EDA tools working environment
# option : iEDA innovus PT dreamPlace
# if "eda_tool" not in os.environ:
#     os.environ['eda_tool'] = "iEDA"
current_dir = os.path.split(os.path.abspath(__file__))[0]
tool_dir = current_dir.rsplit('/', 2)[0]
sys.path.append(tool_dir)
from abc import abstractmethod, ABCMeta
from database.enum import EdaTool, FlowStep, FeatureOption, DSEMethod
from flow.flow_db import DbFlow
from engine.placement import EnginePlacement
from engine.routing import EngineRouting
from engine.net_opt import EngineNetOpt
from engine.timing_opt import EngineTimingOpt
from engine.cts import EngineCTS
from engine.gds import EngineGDS
# from flow.run_flow_ieda import RunFlowIEDA
from application.DSE.parameter import iEDAParameter, InnovusParameter, DREAMPlaceParameter
import wandb
import nni
import optuna
import numpy as np
from feature.io import FeatureIO
import time
import logging
from workspace.path import WorkspacePath
from application.DSE.arguements import Arguements
from application.DSE.config_management import ConfigManagement
import json

class AbstractOptimizationMethod(metaclass=ABCMeta):
    _parameter = None
    _search_config = None
    def __init__(self, args, workspace, parameter, algorithm="TPE", goal="minimize", step=FlowStep.place):
        self._method = algorithm
        self._goal = goal
        self._args = args
        self._workspace = workspace
        self._parameter = parameter
        self._step = step
        self._best_metric = float("inf")
        self.initOptimization()
    
    def getFeatureMetrics(self, data, eda_tool=EdaTool.IEDA, step=FlowStep.place, option=None):
        # evaluation
        eval_io = self.getFeatureIO(eda_tool, step, option=FeatureOption.eval)

        data["evaluation"] = eval_io.get_raw_json()

        place_data = dict()
        feature = self.getFeatureDB()
        hpwl = feature.wirelength.HPWL
        place_data["hpwl"] = hpwl
        if feature.timing:
            wns = feature.timing.FLUTE.clock_timings[0].hold_wns
            place_data["wns"] = wns
            tns = feature.timing.FLUTE.clock_timings[0].hold_tns
            place_data["tns"] = tns
        if len(place_data):
            data["place"] = place_data

        route_feature = self.getFeatureDB(eda_tool=EdaTool.IEDA, step=FlowStep.route, option=FeatureOption.tools)
        # # summary
        # tools_db = self.getFeatureDB(eda_tool, step, option=FeatureOption.tools)
        if route_feature.routing_summary:
            # route_wns = 0
            # route_tns = 0
            # route_freq = 0
            clock = route_feature.routing_summary.la_summary.clocks_timing[0]
            route_wns = clock.setup_wns
            route_tns = clock.setup_tns
            route_freq = clock.suggest_freq
            route_data = dict()
            route_data["route_tns"] = route_tns
            route_data["route_wns"] = route_wns
            route_data["route_freq"] = route_freq
            data["route"] = route_data
        return data

    def getFeatureIO(self, eda_tool=EdaTool.IEDA, step=FlowStep.place, option=FeatureOption.eval):
        io = FeatureIO(dir_workspace = self._workspace,
             eda_tool = eda_tool, 
             feature_option = option,
             flow = DbFlow(eda_tool = eda_tool,step = step))
        io.generate(reload = True)
        return io
    
    def getFeatureDB(self, eda_tool=EdaTool.IEDA, step=FlowStep.place, option=FeatureOption.eval):
        feature = FeatureIO(dir_workspace = self._workspace,
             eda_tool = eda_tool, 
             feature_option = option,
             flow = DbFlow(eda_tool = eda_tool,step = step))
        feature.generate(reload = True)
        db = feature.get_db()
        return db
    
    @abstractmethod
    def logFeature(self, metrics, step):
        raise NotImplementedError

    def setParameter(self, Parameter):
        self._parameter = Parameter
    
    def initOptimization(self):
        self._parameter._search_space = self._parameter.getSearchSpace()
        self.formatSweepConfig()

    @abstractmethod
    def formatSweepConfig(self):
        raise NotImplementedError
    
    @abstractmethod
    def loadParams(self, Parameter):
        raise NotImplementedError

    @abstractmethod
    def runOptimization(self, step=FlowStep.place, option=FeatureOption.tools, metrics={"hpwl": 1.0, "tns": 0.0, "wns": 0.0}, pre_step=FlowStep.cts, tool=EdaTool.IEDA):
        raise NotImplementedError

    @abstractmethod 
    def getNextParams(self):
       raise NotImplementedError
    
    def getPlaceResults(self):
        hpwl,wns,tns,freq = None,None,None,None
        try:
            workspace = self._workspace
            output_dir = os.path.join(workspace, "output/iEDA/data/pl/report/summary_report.txt")
            out_lines = open(output_dir).readlines()
            for i in range(len(out_lines)):
                line = out_lines[i]
                if "Total HPWL" in line:
                    hpwl = line.replace(" ", "").split("|")[-2]
                elif "Late TNS".lower() in line.lower() and "|" in out_lines[i+2]:
                    # print(line)
                    new_line = out_lines[i+2]
                    datas = new_line.replace(" ", "").split("|")
                    # print(datas)
                    wns = datas[-3]
                    tns = datas[-2]
            freq_dir = os.path.join(workspace, "output/iEDA/data/pl/log/info_ipl_glog.INFO") 
            # log_dir = os.path.join(workspace, "output/iEDA/data/pl/log") 
            # curr_time = datetime.now().strftime("%Y%m%d")
            # for file_path in os.listdir(log_dir):
            #     if "info_" in file_path and curr_time in file_path:
            # freq_dir = os.path.join(log_dir, file_path)
            lines = open(freq_dir).readlines()
            for i in range(len(lines)):
                line = lines[i]
                if "Freq(MHz)" in line and "|" in lines[i+2]:
                    next_line = lines[i+2]
                    # print(line)
                    datas = next_line.strip().replace(" ", "").split("|")
                    # print(datas)
                    freq = datas[-2]
                    if wns is None:
                        pass
                    if tns is None:
                        pass
                    break
        except Exception as e:
            print(e)
        return float(hpwl),float(wns),float(tns),float(freq)
    
    def getOperationEngine(self, step, tool, pre_step):
        dir_workspace = self._workspace
        project_name = self._args.project_name
        engine = None
        eda_tool = self.config_manage.getEdaTool()

        if step == FlowStep.floorplan:
            pass
        
        if step == FlowStep.fixFanout:
            pass
            
        if step == FlowStep.place:
            engine = EnginePlacement(dir_workspace = dir_workspace,
                             input_def=f"{dir_workspace}/output/iEDA/result/{project_name}_{pre_step.value}.def.gz",
                             input_verilog = f"{dir_workspace}/output/iEDA/result/{project_name}_{pre_step.value}.v.gz",
                             eda_tool = eda_tool,
                             pre_step = DbFlow(eda_tool = eda_tool,step = pre_step),
                             step = DbFlow(eda_tool = eda_tool,step = step))
        
        if step == FlowStep.cts:
            engine = EngineCTS(dir_workspace = dir_workspace,
                             input_def=f"{dir_workspace}/output/iEDA/result/{project_name}_{pre_step.value}.def.gz",
                             input_verilog = f"{dir_workspace}/output/iEDA/result/{project_name}_{pre_step.value}.v.gz",
                             eda_tool = tool,
                             pre_step = DbFlow(eda_tool = eda_tool,step = pre_step),
                             step = DbFlow(eda_tool = eda_tool,step = step))
            
        if step == FlowStep.optDrv:
            return FlowStep.optDrv
            
        if step == FlowStep.optHold:
            return FlowStep.optHold
            
        if step == FlowStep.optSetup:
            return FlowStep.optSetup
            
        if step == FlowStep.legalization:
            return FlowStep.legalization
            
        if step == FlowStep.route:
            engine = EngineRouting(dir_workspace = dir_workspace,
                             input_def=f"{dir_workspace}/output/iEDA/result/{project_name}_{pre_step.value}.def.gz",
                             input_verilog = f"{dir_workspace}/output/iEDA/result/{project_name}_{pre_step.value}.v.gz",
                             eda_tool = tool,
                             pre_step = DbFlow(eda_tool = eda_tool,step = pre_step),
                             step = DbFlow(eda_tool = eda_tool,step = step))
            
        if step == FlowStep.filler:
            return FlowStep.filler
            
        if step == FlowStep.gds:
            return FlowStep.gds
        
        if step == FlowStep.drc:
            return FlowStep.drc

        return engine

        
class NNIOptimization(AbstractOptimizationMethod):
    _parameter = None
    _search_config = dict()

    def __init__(self, args, workspace, parameter, algorithm="TPE", goal="minimize", step=FlowStep.place):
        super().__init__(args, workspace, parameter, algorithm, goal, step)
    def getNextParams(self):
        return nni.get_next_parameter()
    
    def loadParams(self, Parameter):
        self._parameter = Parameter

    def initOptimization(self):
        super().initOptimization()
        # self.formatSweepConfig()

    def formatSweepConfig(self):
        nni_search_space = self._parameter._search_space
        for key in nni_search_space:
            param = nni_search_space[key]
            if "distribution" in param:
                self._search_config[key] = {
                        "_type": param["distribution"],
                        "_value": [param["min"], param["max"]],
                    }
            else:
                self._search_config[key] = {
                        "_type": "choice",
                        "_value": param["values"],
                    }

    def logPlaceMetrics(self, metrics, results):
        feature = self.getFeatureDB()
        hpwl,wns,tns,freq = self.getPlaceResults()
        messages = ""
        metric = 0.0
        if hpwl is None:
            hpwl = feature.wirelength.HPWL
            wns = feature.timing.FLUTE.clock_timings[0].hold_wns
            tns = feature.timing.FLUTE.clock_timings[0].hold_tns

        hpwl_ref = metrics.get("hpwl", 1.0)
        messages += f"hpwl: {hpwl}, "
        metric += hpwl/hpwl_ref

        messages += f"wns: {wns}, "
        wns_ref = metrics.get("wns", 0.0)
        metric += np.exp(wns_ref)/np.exp(wns)

        messages += f"tns: {tns}, "
        tns_ref = metrics.get("tns", 0.0)
        metric += np.exp(tns_ref)/np.exp(tns)
        
        results["place_hpwl"] = hpwl
        results["place_wns"] = wns
        results["place_tns"] = tns
        results["place_freq"] = freq
        messages += f"place_hpwl: {hpwl}, place_wns: {wns}, place_tns: {tns}, place_freq: {freq}\n"
        logging.info(messages)
        return metric

    def logRouteMetrics(self, metrics, results):
        feature = self.getFeatureDB(eda_tool=EdaTool.IEDA, step=FlowStep.route, option=FeatureOption.tools)
        messages = ""
        metric = 0.0
        if feature.routing_summary:
            if feature.routing_summary.dr_summary:
                route_data = feature.routing_summary.dr_summary.summary[-1][-1]
                print(route_data)
                route_wl = route_data.total_wire_length
                clock = route_data.clocks_timing[-1]
                route_wns = clock.setup_wns
                route_tns = clock.setup_tns
                route_freq = clock.suggest_freq
                messages += f"route_wl: {route_wl}, route_tns: {route_tns}, route_wns: {route_wns}, route_freq: {route_freq}."
                # print(f"route_wl: {route_wl}, route_tns: {route_tns}, route_wns: {route_wns}, route_freq: {route_freq}.")
                metric += route_freq
                results["route_wl"] = route_wl
                results["route_tns"] = route_tns
                results["route_wns"] = route_wns
                results["route_freq"] = route_freq
                if "route_wl" in metrics:
                    metric += route_wl/metrics["route_wl"]
                if "route_tns" in metrics:
                    metric += np.exp(metrics["route_tns"])/np.exp(route_tns)
                if "route_wns" in metrics:
                    metric += np.exp(metrics["route_wns"])/np.exp(route_wns)
                if "route_freq" in metrics:
                    metric += route_freq/metrics["route_freq"]
        logging.info(messages)
        return metric
        
    def logFeature(self, metrics, step):
        metric = 0.0
        results = dict()
          
        if step == FlowStep.place:
            metric = self.logPlaceMetrics(metrics, results)
        else:
            self.logPlaceMetrics(metrics, results)
            metric = self.logRouteMetrics(metrics, results)
        if metric < self._best_metric:
            flow_list = self.config_manage.getFlowList()
            best_config_paths = self.config_manage.getBestConfigPathList()
            self._parameter.dumpOriginalConfig(best_config_paths, flow_list)
        nni.report_final_result(metric)

    def GenerateDataset(self, params, step=FlowStep.place, tool=EdaTool.IEDA):
        # if step==FlowStep.place:
        data = dict()
        data["params"] = params
        data = self.getFeatureMetrics(data, eda_tool=EdaTool.IEDA, step=FlowStep.place, option=None)
        # print(data)
        filepath = f"{self._args.result_dir}/benchmark/{self._args.tech}"
        filename = f"{self._args.result_dir}/benchmark/{self._args.tech}/{self._args.project_name}_{self._step.value}.jsonl"
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        # print(filename)
        with open(filename, "a+") as bf:
            bf.write(json.dumps(data))
            bf.write("\n")
            bf.flush()
    
    def runTask(self, algorithm="TPE", goal="minimize", step=FlowStep.place, tool=EdaTool.IEDA, pre_step=FlowStep.cts):
        dir_workspace = self._workspace
        project_name = self._args.project_name
        engine = self.getOperationEngine(step, tool, pre_step)
        engine.run() 

    def runOptimization(self, step=FlowStep.place, option=FeatureOption.tools, metrics={"hpwl": 1.0, "tns": 0.0, "wns": 0.0}, pre_step=FlowStep.cts, tool=EdaTool.IEDA):
        tt = time.time()
        next_params = self.getNextParams()
        self.config_manage = ConfigManagement(self._args, tool)
        config_paths = self.config_manage.getConfigPathList()
        self._parameter.updateParams(next_params)
        flow_list = self.config_manage.getFlowList()
        self._parameter.dumpOriginalConfig(config_paths, flow_list)
        for db_flow in flow_list:
            step = db_flow.step
            pre_step = db_flow.pre_flow.step
            tool = db_flow.eda_tool
            p = Process(target=self.runTask, args=("bayes", "minimize", step, tool, pre_step)) #实例化进程对象
            p.start()
            p.join()
        self.logFeature(metrics, step)
        self.GenerateDataset(next_params, step, tool)
        total_time = time.time() - tt
        logging.info("task takes %.3f seconds" % (total_time))

class WandbOptimization(AbstractOptimizationMethod):
    _search_config = {
        'method': 'bayes',
        'metric': 
        {
            'goal': 'minimize', 
            'name': 'metric'
        },
        'parameters': None
    }
    def __init__(self, args, workspace, parameter, algorithm="bayes", goal="minimize", step=FlowStep.place):
        super().__init__(args, workspace, parameter, algorithm, goal, step)

    def initOptimization(self):
        # self.formatSweepConfig()
        super().initOptimization()
        sweep_id = wandb.sweep(self._search_config)
        wandb.agent(sweep_id, function=self.runOptimization, count=self._args.run_count)

    def formatSweepConfig(self):
        self._search_config["method"] = self._method 
        self._search_config["metric"]["goal"] = self._goal
        self._search_config["parameters"] = self._parameter._search_space

    def getNextParams(self):
        wandb.init(settings=wandb.Settings(start_method="fork"))
        return wandb.config
    
    def loadParams(self, Parameter):
        self._parameter = Parameter

    def GenerateDataset(self, params, step=FlowStep.place, tool=EdaTool.IEDA):
        # if step==FlowStep.place:
        summary = feature.place_summary
        params["hpwl"] = place.gplace.HPWL 
        params["hpwl"] = place.gplace.wns
        params["hpwl"] = place.gplace.tns
        filepath = f"{self.args.result_dir}/benchmark/{self.args.tech}/{self.args.project_name}.jsonl"
        print(filepath)
        with open(filepath, "a+") as bf:
            bf.write(json.dumps(params))
            bf.write("\n")
            bf.flush()
    
    def runTask(self, algorithm="bayes", goal="minimize", step=FlowStep.place, tool=EdaTool.IEDA, pre_step=FlowStep.cts):
        dir_workspace = self._workspace
        eda_tool = self.config_manage.getEdaTool()
        if step == FlowStep.full_flow:
            flow = RunFlowIEDA(dir_workspace = dir_workspace)
            result = flow.run()
            flow.reset_flow_state()
        else:
            engine = EnginePlacement(dir_workspace = dir_workspace,
                 input_def=f"{dir_workspace}/output/iEDA/result/gcd_legalization.def",
                 input_verilog = f"{dir_workspace}/output/iEDA/result/gcd_legalization.v",
                 eda_tool = eda_tool,
                 pre_step = DbFlow(eda_tool = eda_tool,step = pre_step),
                 step = DbFlow(eda_tool = eda_tool,step = step))
            engine.run()
    
    def logFeature(self, metrics, step):
        feature = self.getFeatureDB()
        place = feature.place_summary
        metric = 0.0
        if "hpwl" in metrics:
            hpwl = place.gplace.HPWL
            wandb.log({"hpwl": hpwl})
            hpwl_ref = metrics["hpwl"]
            metric += hpwl/hpwl_ref
        if "wns" in metrics:
            wns = place.gplace.wns
            wandb.log({"wns": wns})
            wns_ref = metrics["wns"]
            metric += np.exp(wns_ref)/np.exp(wns)
        if "tns" in metrics:
            tns = place.gplace.tns
            wandb.log({"tns": tns})
            tns_ref = metrics["tns"]
            metric += np.exp(tns_ref)/np.exp(tns)
        metric /= len(metrics.keys())
        wandb.log({"metric": metric})
    
    
    def runOptimization(self, step=FlowStep.place, option=FeatureOption.tools, metrics={}, pre_step=FlowStep.cts, tool=EdaTool.IEDA):
        # flow
        tt = time.time()
        next_params = self.getNextParams()
        self._parameter.updateParams(next_params)

        config_manage = ConfigManagement(self.args, eda_tool)
        config_path = config_manage.getConfigPath()
        flow_list = config_manage.getFlowList()
        self._parameter.dumpOriginalConfig(config_path, step, flow_list)
        for db_flow in flow_list:
            step = db_flow.step
            pre_step = db_flow.pre_flow.step
            tool = db_flow.eda_tool
            self.engine = config_manage.getEngine(step)
            p = Process(target=self.runTask, args=("bayes", "minimize", step, tool, pre_step)) #实例化进程对象
            p.start()
            p.join()
        # self.runTask()
        self.logFeature(feature, metrics, step)
        total_time = time.time() - tt
        logging.info("task takes %.3f seconds" % (total_time))
        wandb.log({"total_time": total_time})

if __name__ == "__main__":
    
    tool = os.environ.get('eda_tool', "iEDA")
    args = Arguements.parse(sys.argv[1:])
    parameter = os.environ.get('eda_tool', "iEDA")
    config_manage = ConfigManagement(args, tool)
    step = config_manage.getStep()
    dir_workspace = config_manage.getWorkspacePath()
    eda_tool = config_manage.getEdaTool()

    params = config_manage.getParameters()

    method = NNIOptimization(args, dir_workspace, params, algorithm="TPE", goal="maximize", step=step)
    method.runOptimization(tool=eda_tool, step=step, pre_step=FlowStep.place, metrics={})
    # method.runOptimization(tool=eda_tool, step=step, pre_step=FlowStep.place)