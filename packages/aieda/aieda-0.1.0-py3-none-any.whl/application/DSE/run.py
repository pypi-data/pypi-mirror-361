#search_space = self._search_space
import os
def main():
    search_space = \
    {'init_wirelength_coef': {'_type': 'uniform', '_value': [0.1, 0.5]}, 'min_wirelength_force_bar': {'_type': 'uniform', '_value': [-500.0, -50.0]}, 'target_density': {'_type': 'uniform', '_value': [0.8, 1.0]}, 'bin_cnt': {'_type': 'choice', '_value': [16, 32, 64, 128, 256, 512, 1024]}, 'max_backtrack': {'_type': 'uniform', '_value': [5, 50]}, 'init_density_penalty': {'_type': 'uniform', '_value': [0.0, 0.001]}, 'target_overflow': {'_type': 'uniform', '_value': [0.0, 0.2]}, 'initial_prev_coordi_update_coef': {'_type': 'uniform', '_value': [50.0, 1000.0]}, 'min_precondition': {'_type': 'uniform', '_value': [1.0, 10.0]}, 'min_phi_coef': {'_type': 'uniform', '_value': [0.75, 1.25]}, 'max_phi_coef': {'_type': 'uniform', '_value': [0.75, 1.25]}}

    from nni.experiment import Experiment
    experiment = Experiment('local')

    experiment.config.trial_command = 'python optimization.py --tuner nni' 
    experiment.config.trial_code_directory = os.path.dirname(__file__)
    experiment.config.search_space = search_space

    experiment.config.tuner.name = "TPE"
    experiment.config.tuner.class_args['optimize_mode'] = "minimize"

    experiment.config.max_trial_number = 2000
    experiment.config.trial_concurrency = 40
    experiment.run(5906)
if __name__=="__main__":
    main()