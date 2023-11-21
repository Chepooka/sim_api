import pickle
import sqlite3
import numpy as np


class SparamsDatabaseWriter:
    user_version = 1

    def __init__(self, database):
        # Init database and corresponding api (cursor)
        self.database = sqlite3.connect(database)
        self.database.row_factory = sqlite3.Row
        self.cursor = self.database.cursor()
        # Configure database to efficiently make small transactions
        self.cursor.executescript('''
                                    -- Increment user_version whenever the database schema changes and becomes
                                    -- incompatible with older versions. The reporter should check user_version to
                                    -- see if the database is in the correct format.
                                    PRAGMA user_version=1;
                                    PRAGMA foreign_keys=ON;
                                    CREATE TABLE IF NOT EXISTS Sparams (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        data BLOB NOT NULL,
                                        sweep_parameters BLOB NOT NULL
                                    );
                                    
                                    CREATE TABLE IF NOT EXISTS Configuration (
                                        param_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        sparams_id INTEGER,
                                        parameter_name TEXT NOT NULL,
                                        string_value TEXT,
                                        real_value REAL,
                                        FOREIGN KEY (sparams_id) REFERENCES Sparams(id)
                                    );
                                    CREATE INDEX IF NOT EXISTS idx_config_parameter_name ON Configuration(parameter_name);
                                    CREATE INDEX IF NOT EXISTS idx_config_string_value ON Configuration(string_value);
                                    CREATE INDEX IF NOT EXISTS idx_config_real_value ON Configuration(real_value);
                                    
                                    -- PRAGMA user_version; -- check if we're using a database with the correct schema
                                    ''')
        self.database.commit()

    def add_parameter_config(self, sparams_id, key, value):
        if type(value) == str:
            column_id = 'string_value'
        else:
            column_id = 'real_value'
            value = float(value)

        self.cursor.execute(
            f'INSERT INTO Configuration (sparams_id, parameter_name, {column_id}) VALUES (?, ?, ?)',
            (sparams_id, key, value))

    def serialize_array(self, array):
        return pickle.dumps((array.tobytes(), array.shape, array.dtype))

    def add_sparams(self, sparams, sweep_parameters, config):

        self.cursor.execute('INSERT INTO Sparams(data, sweep_parameters) VALUES (?, ?)',
                            (sqlite3.Binary(self.serialize_array(sparams)),
                             sqlite3.Binary(self.serialize_array(sweep_parameters))))
        sparams_id = self.cursor.lastrowid

        for key, value in config.items():
            self.add_parameter_config(sparams_id, key, value)

        self.database.commit()

    def close(self):
        self.cursor.close()
        self.database.close()
