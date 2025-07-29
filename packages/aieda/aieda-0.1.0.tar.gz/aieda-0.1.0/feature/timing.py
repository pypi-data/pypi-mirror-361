#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   timing.py
@Time    :   2024/10/10 14:54:56
@Author  :   Dawn Li
@Version :   1.0
@Contact :   dawnli619215645@gmail.com
@Desc    :   Timing Feature Parser
'''


from typing import Dict
import json
import os
import sys
import logging

if True:
    current_dir = os.path.split(os.path.abspath(__file__))[0]
    tool_dir = current_dir.rsplit('/', 1)[0]
    sys.path.append(tool_dir)

    from tools.innovus.feature.database.tools import PowerINNOVUSBase, TimingINNOVUSBase, FeatureTimingINNOVUS
    from tools.iEDA.feature.database.eval import FeatureTimingIEDA, MethodTimingIEDA, FeatureTimingEnumIEDA, FeatureEval
    from tools.iEDA.feature.database.tools import ClockTiming
    from database.timing import FeatureTiming
    from database.enum import EdaTool, FeatureOption
    from flow.flow_db import DbFlow
    from feature.io import FeatureIO, FeatureOption, FlowStep
    from workspace.path import WorkspacePath
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logging.basicConfig(
    level=logging.WARNING,
    format=f'%(asctime)s [\033[95m%(levelname)s\033[0m] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)


class FeatureTimingBase(object):
    def __init__(self, dir_workspace: str, eda_tool: EdaTool, step: FlowStep):
        self.dir_workspace = dir_workspace
        self.eda_tool = eda_tool
        self.step = step
        self.workspace = WorkspacePath(dir_workspace)


class FeatureTimingGenerator(FeatureTimingBase):
    def __init__(self, dir_workspace: str, eda_tool: EdaTool, step: FlowStep):
        super().__init__(dir_workspace, eda_tool, step)

    def generateFeatureTimingIEDA(self, eval_path: str) -> FeatureTimingIEDA:
        """generate timing feature from timing eval ieda

        Args:
            eval_path (str): path of timing eval ieda

        Returns:
            Timing: Timing Feature
        """
        if not os.path.exists(eval_path):
            logging.warning(f"{eval_path} not found")
            return None
        # Initialize MethodTiming instances for each method
        method_timing_dict: Dict[str, MethodTimingIEDA] = {}
        for method in FeatureTimingEnumIEDA:
            method_timing_dict[method.value] = MethodTimingIEDA([], 0, 0)

        with open(eval_path, 'r') as file:
            for line in file:
                data = json.loads(line.strip())
                if 'Timing' in data:
                    timing_data = data['Timing']
                    for method_name, timing_entries in timing_data.items():
                        # Check if method_name is one of the expected methods
                        if method_name in method_timing_dict:
                            method_timing = method_timing_dict[method_name]
                            for timing_entry in timing_entries:
                                # Create a TimingData instance for each clock
                                timing_data_obj = ClockTiming(
                                    clock_name=timing_entry['clock_name'],
                                    hold_tns=timing_entry['hold_tns'],
                                    hold_wns=timing_entry['hold_wns'],
                                    setup_tns=timing_entry['setup_tns'],
                                    setup_wns=timing_entry['setup_wns'],
                                    suggest_freq=timing_entry['suggest_freq']
                                )
                                method_timing.clock_timings.append(
                                    timing_data_obj)
                elif 'Power' in data:
                    power_data = data['Power']
                    for method_name, power_entry in power_data.items():
                        # Check if method_name is one of the expected methods
                        if method_name in method_timing_dict:
                            method_timing = method_timing_dict[method_name]
                            method_timing.dynamic_power = power_entry['dynamic_power']
                            method_timing.static_power = power_entry['static_power']

        # Create the Timing instance with the collected data
        timing_ieda = FeatureTimingIEDA()
        for method_name, method_timing in method_timing_dict.items():
            setattr(timing_ieda, method_name, method_timing)

        return timing_ieda

    def generateFeatureTimingINNOVUS(self, sta_path, power_path) -> FeatureTimingINNOVUS:
        timing = TimingINNOVUSBase()
        power = PowerINNOVUSBase()

        if not os.path.exists(sta_path):
            print(f"\033[35mWarning: {sta_path} not found\033[0m")
            return None
        if not os.path.exists(power_path):
            print(f"\033[35mWarning: {power_path} not found\033[0m")
            return None

        with open(sta_path, 'r') as file:
            data = json.load(file)
            timing.WNS = data['sta']['WNS']
            timing.TNS = data['sta']['TNS']
            timing.violation_paths = data['sta']['Violating Paths']
            timing.max_cap = data['sta']['max_cap']
            timing.max_tran = data['sta']['max_tran']
            timing.max_fanout = data['sta']['max_fanout']
            timing.max_length = data['sta']['max_length']
            timing.density = data['sta']['Density']
            timing.frequency = data['frequency']

        with open(power_path, 'r') as file:
            data = json.load(file)
            factor = 1e-3  # convert mW to W
            power.internal_power = data['power']['internal_power'] * factor
            power.switch_power = data['power']['switch_power'] * factor
            power.leakage_power = data['power']['leakage_power'] * factor
            power.total_power = data['power']['total_power'] * factor

        timing_innovus = FeatureTimingINNOVUS(timing=timing, power=power)
        return timing_innovus

    def convertFeatureTimingIEDA(self, timing_ieda: FeatureTimingIEDA, method: FeatureTimingEnumIEDA = FeatureTimingEnumIEDA.FLUTE) -> FeatureTiming:
        timing_feature = FeatureTiming()
        if timing_ieda is None:
            logging.warning(
                f"timing_ieda is None, dir_workspace: {self.dir_workspace}")
            return timing_feature
        method_timing: MethodTimingIEDA = getattr(timing_ieda, method.value)
        clock_timing: ClockTiming = method_timing.clock_timings[0]
        timing_feature.WNS = clock_timing.setup_wns
        timing_feature.TNS = clock_timing.setup_tns
        timing_feature.suggest_freq = clock_timing.suggest_freq
        timing_feature.dynamic_power = method_timing.dynamic_power
        timing_feature.static_power = method_timing.static_power
        return timing_feature

    def convertFeatureTimingINNOVUS(self, timing_innovus: FeatureTimingINNOVUS) -> FeatureTiming:
        timing_feature = FeatureTiming()
        if timing_innovus is None:
            logging.warning(
                f"timing_innovus is None, dir_workspace: {self.dir_workspace}")
            return timing_feature
        if timing_innovus.timing is None:
            logging.warning(
                f"timing_innovus.timing is None, dir_workspace: {self.dir_workspace}")
            return timing_feature
        timing_feature.WNS = timing_innovus.timing.WNS
        timing_feature.TNS = timing_innovus.timing.TNS
        timing_feature.suggest_freq = timing_innovus.timing.frequency
        if timing_innovus.power is None:
            logging.warning(
                f"timing_innovus.power is None, dir_workspace: {self.dir_workspace}")
            return timing_feature
        timing_feature.dynamic_power = timing_innovus.power.internal_power + \
            timing_innovus.power.switch_power
        timing_feature.static_power = timing_innovus.power.leakage_power
        return timing_feature

    def getFeatureTiming(self) -> FeatureTiming:
        if self.eda_tool == EdaTool.IEDA:
            return self.getFeatureTimingFromIEDA()
        elif self.eda_tool == EdaTool.INNOVUS:
            return self.getFeatureTimingFromINNOVUS()

    def getFeatureTimingFromIEDA(self) -> FeatureTiming:
        feature_io = FeatureIO(dir_workspace=self.dir_workspace,
                               eda_tool=self.eda_tool,
                               feature_option=FeatureOption.eval,
                               flow=DbFlow(eda_tool=self.eda_tool, step=self.step))
        feature_db: FeatureEval = feature_io.get_db_ieda()
        feature = self.convertFeatureTimingIEDA(feature_db)
        return feature

    def getFeatureTimingFromINNOVUS(self) -> FeatureTiming:
        if(self.eda_tool == EdaTool.IEDA):
            # HARD CODE: eda_tool=EdaTool.IEDA
            timing_feature_io = FeatureIO(dir_workspace=self.dir_workspace,
                                          eda_tool=self.eda_tool,
                                          feature_option=FeatureOption.baseline_sta,
                                          flow=DbFlow(eda_tool=self.eda_tool, step=self.step))
            timing_db: TimingINNOVUSBase = timing_feature_io.get_db_ieda()
    
            # HARD CODE: eda_tool=EdaTool.IEDA
            power_feature_io = FeatureIO(dir_workspace=self.dir_workspace,
                                         eda_tool=self.eda_tool,
                                         feature_option=FeatureOption.baseline_power,
                                         flow=DbFlow(eda_tool=self.eda_tool, step=self.step))
            power_db: PowerINNOVUSBase = power_feature_io.get_db_ieda()
    
            feature_db = FeatureTimingINNOVUS(timing=timing_db, power=power_db)
            feature = self.convertFeatureTimingINNOVUS(feature_db)
            return feature
        
        if(self.eda_tool == EdaTool.INNOVUS):
            timing_feature_io = FeatureIO(dir_workspace=self.dir_workspace,
                                          eda_tool=self.eda_tool,
                                          feature_option=FeatureOption.tools,
                                          flow=DbFlow(eda_tool=self.eda_tool, step=self.step))
            
            timing_db = None
            power_db = None

            if(self.step == FlowStep.place):
                timing_db, power_db, db_hotspot = timing_feature_io.get_db_innovus()
            if(self.step == FlowStep.cts):
                timing_db, power_db = timing_feature_io.get_db_innovus()
            if(self.step == FlowStep.route):
                timing_db, power_db = timing_feature_io.get_db_innovus()

            feature_db = FeatureTimingINNOVUS(timing=timing_db, power=power_db)
            feature = self.convertFeatureTimingINNOVUS(feature_db)
            
            return feature
        
        return None


if __name__ == "__main__":

    def get_ieda_eval_path(case_name, step):
        return os.path.join("/data/project_share/dataset_baseline/", case_name, "workspace/output/iEDA/feature/", f"{case_name}_{step}_eval.jsonl")

    def get_innovus_power_path(case_name, step):
        return os.path.join("/data/project_share/dataset_baseline/", case_name, "workspace/output/iEDA/feature/", f"{case_name}_{step}_baseline_power.json")

    def get_innovus_sta_path(case_name, step):
        return os.path.join("/data/project_share/dataset_baseline/", case_name, "workspace/output/iEDA/feature/", f"{case_name}_{step}_baseline_sta.json")

    def get_workspace_path(case_name):
        return os.path.join("/data/project_share/dataset_baseline/", case_name, "workspace")

    test_case = "aes"
    test_step = "place"
    feature_parser = FeatureTimingGenerator(
        dir_workspace=get_workspace_path(test_case), eda_tool=EdaTool.IEDA, step=FlowStep.place)

    ieda_timing_feature: FeatureTimingIEDA = feature_parser.generateFeatureTimingIEDA(
        get_ieda_eval_path(test_case, test_step))

    logging.info(f"iEDA Feature:\n{ieda_timing_feature}")

    innovus_timing_feature = feature_parser.generateFeatureTimingINNOVUS(
        get_innovus_sta_path(test_case, test_step), get_innovus_power_path(test_case, test_step))

    logging.info(f"INNOVUS Feature:\n{innovus_timing_feature}")

    feature_ieda = feature_parser.convertFeatureTimingIEDA(
        ieda_timing_feature)

    logging.info(f"Timing Feature built from iEDA:\n{feature_ieda}")

    feature_innovus = feature_parser.convertFeatureTimingINNOVUS(
        innovus_timing_feature)

    logging.info(f"Timing Feature built from INNOVUS:\n{feature_innovus}")
