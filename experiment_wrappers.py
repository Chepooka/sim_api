from datetime import datetime


class Experiment:
    def __init__(self, experiment_type, experiment_name):
        self.experiment_type = experiment_type
        self.experiment_name = experiment_name
        self.time_stamp = datetime.now().isoformat()

    def add_config_parameter(self, name, value):
        setattr(type(self), name, value)

    def get_config(self):
        return {'experiment_name': self.experiment_name, 'time_stamp': self.time_stamp,
                'experiment_type': self.experiment_type}


class BOExperiment(Experiment):
    def __init__(self, experiment_name, param_names, param_ranges, experiment_type='BO'):
        super(BOExperiment, self).__init__(experiment_type, experiment_name)
        self.param_names = param_names
        self.param_ranges = param_ranges

    def get_config(self):
        config = super(BOExperiment, self).get_config()

        for i, param_name in enumerate(self.param_names):
            config[param_name + '_min'] = self.param_ranges[0][i]
            config[param_name + '_max'] = self.param_ranges[1][i]

        return config


class RBOExperiment(BOExperiment):
    def __init__(self, experiment_name, param_names, param_ranges):
        super(RBOExperiment, self).__init__(experiment_name, param_names, param_ranges, 'RBO')


class ParameterSweep(Experiment):
    def __init__(self, experiment_name, param_name, param_range):
        super(ParameterSweep, self).__init__('parameter_sweep', experiment_name)
        self.param_name = param_name
        self.param_range = param_range

    def get_config(self):
        config = super(ParameterSweep, self).get_config()

        config[self.param_name + '_min'] = self.param_range[0]
        config[self.param_name + '_max'] = self.param_range[1]

        return config


