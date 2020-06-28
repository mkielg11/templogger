import os
import sqlite3
from threading import Lock
from datetime import datetime

import pandas as pd

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


class HTDataBaseHandler:
    TABLE_NAME = 'HT_DATA'
    TABLE_COLUMNS = (('device', 'text'),
                     ('date', 'text'),
                     ('temperature decigrades', 'integer'),
                     ('humidity promille', 'integer'),
                     ('battery status', 'integer'))

    def __init__(self, path=None):
        if path is None:
            path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'ht_data.db')
        self._db_access_lock = Lock()
        with self._db_access_lock:
            self.db_exists = os.path.exists(path)
            self.db_connection = sqlite3.connect(path, check_same_thread=False)

        if not self.db_exists:
            self._init_database()

    def close(self):
        if self.db_connection:
            self.db_connection.close()

    def __del__(self):
        self.close()

    def _init_database(self):
        with self._db_access_lock:
            c = self.db_connection.cursor()

            # Create table
            column_definitions = ','.join([' '.join(column) for column in self.TABLE_COLUMNS])
            c.execute('CREATE TABLE {} ({})'.format(self.TABLE_NAME, column_definitions))

            # Save (commit) the changes
            self.db_connection.commit()
        self.db_exists = True

    def write_row(self, device, date, temperature, humidity, battery_status):
        if not self.db_exists:
            self._init_database()
        with self._db_access_lock:

            c = self.db_connection.cursor()
            c.execute("INSERT INTO {} VALUES ('{}','{}',{},{},{})"
                      .format(self.TABLE_NAME, device, date.strftime(DATETIME_FORMAT),
                              int(round(temperature*10)), int(round(humidity*10)), battery_status))

            self.db_connection.commit()

    def get_data(self):
        with self._db_access_lock:
            df = pd.read_sql_query("SELECT * from "+self.TABLE_NAME, self.db_connection)
        df['date'] = pd.to_datetime(df['date'], format=DATETIME_FORMAT)
        if 'temerature' in df.columns:
            # Handle typo
            df = df.rename(columns={'temerature': 'temperature', }, errors="raise")
        df['temperature'] = df['temperature'].astype(float) / 10
        df['humidity'] = df['humidity'].astype(float) / 10
        return df

    def clean_database(self):
        with self._db_access_lock:
            # Get a cursor object
            cursor = self.db_connection.cursor()

            # Execute the DROP Table SQL statement
            cursor.execute('DROP TABLE ' + self.TABLE_NAME)
            self.db_connection.commit()

        self.db_exists = False
        self._init_database()


def db_test():
    db_handler = HTDataBaseHandler()
    db_handler.clean_database()
    db_handler.write_row('HT_TEST', datetime.now(), 25.4, 51.0, 99)


if __name__ == '__main__':
    db_test()
