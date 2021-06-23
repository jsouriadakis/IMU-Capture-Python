import mysql.connector
from mysql.connector import errorcode

import json

config = {
    "user": "root",
    "password": "",
    "host": "127.0.0.1",
    "port": "3306",
    "database": "automatic_gym",
    "raise_on_warnings": True,
    "use_pure": True,
}


def open_database():
    try:
        connection = mysql.connector.connect(**config)
        return connection

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        connection.close()


class MySqlClass:
    connection = None
    cursor = None

    def start_connection(self):

        self.connection = open_database()
        self.cursor = self.connection.cursor()

    def close_database(self):
        self.connection.close()
        self.cursor.close()

    def getAllSensorData(self, current_id):
        try:
            # make it read the next index if current_id == -1
            self.connection.commit()
            if current_id == -1:
                self.cursor.execute("SELECT * FROM sensor_data ORDER BY id DESC LIMIT 1")
            else:
                self.cursor.execute("SELECT * FROM automatic_gym.sensor_data  where id = " + str(current_id + 1))
            record = self.cursor.fetchone()
            if record is None:
                return None
            index, user_id, device_id, time, time2, weight, distance, accelerometer_array, gyroscope_array = record
            if index > current_id:
                return index, user_id, device_id, time, time2, weight, distance, json.loads(
                    accelerometer_array), json.loads(gyroscope_array)
            else:
                pass

        except mysql.connector.Error as error:
            print("Failed to read search links. Error:{}".format(error))
