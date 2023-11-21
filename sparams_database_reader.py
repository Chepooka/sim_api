import sqlite3
import pickle
import numpy as np


class SparamsDatabaseReader:
    user_version = 1

    def __init__(self, database):
        # Init database and corresponding api (cursor)
        self.database = sqlite3.connect(database)
        self.database.row_factory = sqlite3.Row
        self.cursor = self.database.cursor()
        # Configure database to efficiently make small transactions
        self.cursor.execute('''PRAGMA user_version''')
        user_version = self.cursor.fetchall()[0]["user_version"]
        if user_version != self.user_version:
            raise ValueError("Database user version mismatch.")

    def get_record_id_and_value(self, record):
        id = record['sparams_id']
        value = record['string_value']
        if value is None:
            value = record['real_value']
        if value is None:
            raise ValueError
        return id, value

    def get_parameter_by_name(self, parameter_name):
        self.cursor.execute(f'''SELECT * FROM Configuration WHERE parameter_name = \'{parameter_name}\'''')
        records = self.cursor.fetchall()
        ids = []
        values = []

        for record in records:
            id, value = self.get_record_id_and_value(record)
            ids.append(id)
            values.append(value)

        return ids, values

    def get_config(self, filter=None):

        if filter is None or (type(filter) is dict and len(filter.keys()) == 0):
            records = self.cursor.execute('''SELECT * FROM Configuration ORDER BY sparams_id;''')
        elif type(filter) is dict:
            filter_str = self.get_filter_str(filter)
            self.cursor.execute('''SELECT * FROM Configuration WHERE sparams_id IN (SELECT sparams_id FROM Configuration ''' + filter_str + f'''GROUP BY sparams_id HAVING 
            COUNT(DISTINCT parameter_name) = {len(filter.keys())}) ORDER BY sparams_id;''')
            records = self.cursor.fetchall()
        else:
            raise TypeError

        if len(records) == 0:
            return {}

        dict_list = []
        id_prev = -1

        for record in records:
            id, value = self.get_record_id_and_value(record)
            if id_prev == -1:
                config_dict = {'sparams_id': id}
            elif id != id_prev:
                dict_list.append(config_dict)
                config_dict = {'sparams_id': id}
            id_prev = id
            config_dict[record['parameter_name']] = value
        dict_list.append(config_dict)

        return dict_list

    def get_sparams(self, filter):

        config = self.get_config(filter)

        sparams_ids = []

        for config_dict in config:
            sparams_ids.append(config_dict['sparams_id'])

        self.cursor.execute(f'''SELECT * FROM Sparams WHERE id IN ({', '.join(map(str, sparams_ids))}) ORDER BY id;''')
        records = self.cursor.fetchall()

        if len(records) != len(config):
            raise ValueError

        for i, config_dict in enumerate(config):
            serialized_data, shape, dtype = pickle.loads(records[i]['data'])
            config_dict['sparams'] = np.frombuffer(sqlite3.Binary(serialized_data), dtype=dtype).reshape(shape)
            serialized_data, shape, dtype = pickle.loads(records[i]['sweep_parameters'])
            config_dict['sweep_parameters'] = np.frombuffer(sqlite3.Binary(serialized_data), dtype=dtype).reshape(shape)

        return config

    def get_filter_str(self, config, tol=1e-6):
        filter_list = []
        for key, value in config.items():
            if type(value) is str:
                filter_str = f'(parameter_name=\'{key}\' AND string_value=\'{value}\')'
            else:
                filter_str = f'(parameter_name=\'{key}\' AND real_value BETWEEN \'{value - tol:.16f}\' AND \'{value + tol:.16f}\')'
            filter_list.append(filter_str)

        return 'WHERE ' + ' OR '.join(filter_list)
