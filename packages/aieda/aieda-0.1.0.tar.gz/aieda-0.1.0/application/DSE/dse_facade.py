#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   dse_facade.py
@Time    :   2024-08-29 10:54:34
@Author  :   SivanLaai
@Version :   1.0
@Contact :   lyhhap@163.com
@Desc    :   dse facade
'''

import sys
import os

current_dir = os.path.split(os.path.abspath(__file__))[0]
tool_dir = current_dir.rsplit('/', 2)[0]
print(tool_dir)
sys.path.append(tool_dir)
import time
import logging
import datetime
import os
import sys
import json
from application.DSE.arguements import Arguements
from application.DSE.config_management import ConfigManagement
from database.enum import EdaTool, FlowStep, DSEMethod
from application.DSE.optimization import WandbOptimization, NNIOptimization
from workspace.path import WorkspacePath
import wandb
import yaml


class DSEFacade:
    params = None
    def objective(self, trial):
        return self.start(trial=trial)

    def run_optuna(self):
        study = None
        sampler = optuna.samplers.TPESampler()
        study = optuna.create_study(storage="mysql+pymysql://username:password@ip:port/optuna", study_name=self.args.project_name, \
                                     directions=["minimize", "maximize", "maximize"], sampler=sampler, load_if_exists=True)
        if not study:
            return
        study.optimize(self.objective, n_trials=100, timeout=None)

        pruned_trials = study.get_trials(deepcopy=False, states=[TrialState.PRUNED])
        complete_trials = study.get_trials(deepcopy=False, states=[TrialState.COMPLETE])

        print("Study statistics: ")
        print("  Number of finished trials: ", len(study.trials))
        print("  Number of pruned trials: ", len(pruned_trials))
        print("  Number of complete trials: ", len(complete_trials))

        print("Best trial:")
        trials = study.best_trials

        for trial in trials:
            print("  Value: ", trial)

            print("  Params: ")
            for key, value in trial.params.items():
                print("    {}: {}".format(key, value))

    def run_nni(self, algorithm="TPE", direction="minimize", search_space=dict(), concurrency=1, max_trial_number=2000, flows=None):
        from nni.experiment import Experiment
        import random
        experiment = Experiment('local')
        port = 8088
        # print(vars(self.args))


        try:
            # trial_command = f'python optimization.py --tuner nni --step {self.step.value.lower()} --flows {flows}'
            arg_setting = ""
            for k,v in vars(self.args).items():
               if isinstance(v, bool):
                   if v:
                       arg_setting += f" --{k}"
               elif v is not None:
                   arg_setting += f" --{k} {v}"
            # print(arg_setting)
            trial_command = f'python optimization.py {arg_setting}'
            print(trial_command)
            experiment.config.trial_command = trial_command 
            experiment.config.trial_code_directory = os.path.dirname(__file__)
            experiment.config.search_space = search_space

            experiment.config.tuner.name = algorithm
            experiment.config.tuner.class_args['optimize_mode'] = direction

            experiment.config.max_trial_number = self.args.run_count
            experiment.config.trial_concurrency = self.args.sweep_worker_num
            experiment.run(port)
            # experiment.run(random.Random().randint(3000, 60036))
        except Exception as e:
            print(e)
            port = random.Random().randint(3000, 60036)
            experiment.run(port)
            # print(arg_setting)

    def start(self, optimize=DSEMethod.WANDB, eda_tool=EdaTool.IEDA, step=FlowStep.place):
        self.args = Arguements.parse(sys.argv[1:])
        config_manage = ConfigManagement(self.args, eda_tool)
        self.step = config_manage.getStep()
        # self.config_paths = config_manage.getConfigPathList()
        dir_workspace = config_manage.getWorkspacePath()

        self.params = config_manage.getParameters()

        os.environ["OMP_NUM_THREADS"] = "%d" % (self.params.num_threads)

        if optimize==DSEMethod.WANDB:
            self.setEnv(self.args)
            method = WandbOptimization(self.args, dir_workspace, self.params, self.step)
            method.runOptimization(tool=parameter)
        elif optimize==DSEMethod.NNI:
            method = NNIOptimization(self.args, dir_workspace, self.params, self.step)
            self._search_space = method._search_config
            print(self._search_space)
            self.run_nni(search_space=self._search_space, flows=self.args.flows)
        elif optimize==DSEMethod.OPTUNA:
            pass

    def setEnv(self, args):
        os.environ["WANDB_PROJECT"] = args.project_name
        os.environ["WANDB_MODE"] = args.wandb_mode



if __name__ == "__main__":
    auto = DSEFacade(None) 
    auto.start(optimize=DSEMethod.NNI)