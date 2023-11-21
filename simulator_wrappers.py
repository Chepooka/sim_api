import numpy as np
from ipkiss3 import all as i3
from datetime import datetime
from experiment_wrappers import Experiment
from sparams_database_writer import SparamsDatabaseWriter


class Simulator:
    def __init__(self, method, experiment_info, db_file):
        self.method = method
        if isinstance(experiment_info, Experiment):
            self.experiment_info = experiment_info.get_config()
        elif type(experiment_info) is dict:
            self.experiment_info = experiment_info
        self.database = SparamsDatabaseWriter(db_file)

    def _simulate_geometry(self, layout):
        pass

    def simulate_geometry(self, device_geometry):
        start_time = datetime.now().isoformat()
        sparams, sweep_params = self._simulate_geometry(device_geometry)
        stop_time = datetime.now().isoformat()
        self.save_results(sparams, sweep_params, device_geometry, start_time, stop_time)

    def save_results(self, sparams, sweep_params, device_geometry, start_time, stop_time):
        config = device_geometry.get_config()
        config.update(self.experiment_info)
        config.update(self.get_config())
        config['start_time'] = start_time
        config['stop_time'] = stop_time
        self.database.add_sparams(sparams, sweep_params, config)

    def get_config(self):
        return {'method': self.method}


class FDTDSimulator(Simulator):
    def __init__(self, experiment_info, db_file, wl_min, wl_max, nwls, mesh_accuracy):
        super(FDTDSimulator, self).__init__('FDTD', experiment_info, db_file)
        self.wl_min = wl_min
        self.wl_max = wl_max
        self.nwls = nwls
        self.mesh_accuracy = mesh_accuracy
        self.sweep_param_type = 'wavelength'
        self.sweep_param_unit = 'nm'

    def _simulate_geometry(self, geometry):
        layout = geometry.get_layout()

        # make sure the ports don’t fall at the edge of the simulation region by extending the waveguides
        sim_geom = i3.device_sim.SimulationGeometry(layout=layout, waveguide_growth=0.1)

        # define simulation
        sim_name = f'smatrix'
        simulation = i3.device_sim.LumericalFDTDSimulation(
            geometry=sim_geom,
            outputs=[i3.device_sim.SMatrixOutput(name=sim_name, wavelength_range=(self.wl_min, self.wl_max, self.nwls),
                                                 symmetries=geometry.symmetries)],
            setup_macros=[i3.device_sim.lumerical_macros.fdtd_mesh_accuracy(self.mesh_accuracy)])
        result = simulation.get_result(name=sim_name)

        port_mapping = {}
        for key, val in result.term_mode_map.items():
            port_mapping[key[0].strip(' ')] = val
        smatrix = np.zeros_like(result.data)
        nports = len(geometry.port_map)
        for i in range(nports):
            for j in range(nports):
                smatrix[i, j, :] = result.data[port_mapping[geometry.port_map[i]], port_mapping[geometry.port_map[j]], :]
        wavelengths = result.sweep_parameter_values

        return smatrix, wavelengths

    def get_config(self):
        config = super(FDTDSimulator, self).get_config()
        config.update({'wl_min': self.wl_min, 'wl_max': self.wl_max, 'nwls': self.nwls,
                       'mesh_accuracy': self.mesh_accuracy, 'sweep_param_type': self.sweep_param_type,
                       'sweep_param_unit': self.sweep_param_unit})
        return config