import os
import numpy as np

from sparams_database_reader import SparamsDatabaseReader
from sparams_database_writer import SparamsDatabaseWriter

if __name__ == '__main__':

    # initialize database
    db_writer = SparamsDatabaseWriter('db')

    # add S-parameters
    sweep_params = np.arange(3, dtype=np.float64)
    sparams = np.arange(27, dtype=np.complex128)
    sparams.shape = (3, 3, 3)
    config = {'param1': 5.123, 'param2': 2, 'sweep_param_type': 'frequency', 'sweep_param_unit': 'THz'}
    db_writer.add_sparams(sparams, sweep_params, config)

    config = {'param1': 5.123, 'param2': 1, 'sweep_param_type': 'wavelength', 'sweep_param_unit': 'THz'}
    db_writer.add_sparams(10*sparams, sweep_params, config)

    sparams = 2 * np.arange(27, dtype=np.complex128)
    sparams.shape = (3, 3, 3)
    config = {'param1': 4}
    db_writer.add_sparams(sparams, sweep_params, config)

    sparams = 3 * np.arange(27, dtype=np.complex128)
    sparams.shape = (3, 3, 3)
    config = {'param1': 5.1}
    db_writer.add_sparams(sparams, sweep_params, config)

    # init reader
    db_reader = SparamsDatabaseReader('db')

    # read parameter
    #db_reader.get_sparams(config)


    # read S-parameters

    #ids, values = db_reader.get_parameter_by_name('param1')

    dict_list = db_reader.get_sparams({'param1': 5.123})

    #dict_list = db_reader.get_config()
    for dict in dict_list:
        print(dict['sparams'])
        print(dict['sweep_parameters'])

    # close connection
    db_writer.close()


