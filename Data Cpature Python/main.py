import database as db
from database import MySqlClass
from dataClass import SensorData, Filter
from queue import Queue
import numpy as np
import pandas as pd
from repetition import RepetitionClass
import matplotlib.pyplot as plt
import csv
import time

sql = MySqlClass()
rep = RepetitionClass()
chooseFilter = Filter()
queueSize = 300
fileNameIndex = 1

def main():
    frame = 1000
    rolling = 0
    current_id = -1
    sensors = Queue(maxsize=queueSize)
    sensors2 = Queue(maxsize=300)
    sql.start_connection()
    acceleration = []
    gyroscope = []
    accelerationT = []
    gyroscopeT = []
    timing = []
    timeFrame = 0
    timeStart = 0
    timeEnd = 0
    timeBetweenSample = 0
    peaksValue = []
    initialQ = [1.0, 0.0, 0.0, 0.0]
    x = 0
    fig = plt.figure()
    ax = fig.add_subplot(111)
    count = 0
    while True:
        if sql.getAllSensorData(current_id) is not None:
            index, user_id, device_id, time, time2, weight, distance, accelerometer_array, gyroscope_array = sql.getAllSensorData(
                current_id)
            current_id = index
            mySensor = SensorData(index, user_id, device_id, time, time2, weight, distance, accelerometer_array, gyroscope_array, initialQ)
            if not sensors.full():
                count = count + 1
                print(count)
                sensors.put(mySensor)
                initialQ = mySensor.returnLastQ()
        else:
            if sensors.full():
                sensorList = list(sensors.queue)
                if len(acceleration) == 0:
                    for sensor in sensorList:
                        accel, accelT, gyro, gyroT, tim = sensor.returnAccGyroTime()
                        if len(acceleration) == 0:
                            timeStart = sensor.time
                            acceleration = np.copy(accel)
                            gyroscope = np.copy(gyro)
                            accelerationT = np.copy(accelT)
                            gyroscopeT = np.copy(gyroT)
                            timing = np.copy(tim)

                        else:
                            timeEnd = sensor.time2
                            acceleration = np.concatenate((acceleration, accel), axis=1)
                            gyroscope = np.concatenate((gyroscope, gyro), axis=1)
                            accelerationT = np.concatenate((accelerationT, accelT), axis=1)
                            gyroscopeT = np.concatenate((gyroscopeT, gyroT), axis=1)
                            timing = np.concatenate((timing, tim), axis=0)
                            #timing = np.concatenate((timing, tim),axis = 0
                # else:
                #     sensor = sensorList[len(sensorList)-1]
                #     timeStart = sensorList[0].time
                #     timeEnd = sensor.time2
                #     accel, accelT, gyro, gyroT, tim = sensor.returnAccGyroTime()
                #     acceleration = np.concatenate((acceleration, accel), axis=1)
                #     gyroscope = np.concatenate((gyroscope, gyro), axis=1)
                #     accelerationT = np.concatenate((accelerationT, accelT), axis=1)
                #     gyroscopeT = np.concatenate((gyroscopeT, gyroT), axis=1)
                #     timing += tim
                #     # timing = np.concatenate((timing, tim),axis = 0
                #     acceleration = acceleration[:, 10:]
                #     gyroscope = gyroscope[:, 10:]
                #timeFrame = timeEnd - timeStart
                #samples = acceleration.shape[1]
                #sampleRate = frame*samples/timeFrame
                #indices, reps = rep.countReps(distance, sampleRate)
                # if len(indices) == 0:
                #     if len(peaksValue) != 0:
                #         peaksValue = []
                #     #print("empty")
                # else:
                #     print(indices)
                #     for index in indices:
                #
                #         peaksValue.append(index)
                #         #print(peaksValue)
                # #acceleration = []
                # #gyroscope = []
                writeFile(timing, acceleration, gyroscope, accelerationT, gyroscopeT)
                while not sensors.empty():
                    sensors.get()
                acceleration = []
                gyroscope = []
                accelerationT = []
                gyroscopeT = []
                timing = []
                current_id = -1
                #sensors.get()

            # if sensors2.full():
            #
            #     for sensor in list(sensors2.queue):
            #         x = x + 10
            #         accel, gyro = sensor.returnAccAndGyro()
            #         if len(acceleration2) == 0:
            #             acceleration2 = np.copy(accel)
            #
            #         else:
            #             acceleration2 = np.concatenate((acceleration2, accel), axis=1)
            #     t = []
            #     for i in range(0,x):
            #         t.append(i)
            #     ax.clear()
            #     ax.plot(t, acceleration2[2])
            #     plt.show()
            #     acceleration2 = []
            #     #for i in range(0, len(acceleration2)):
            #
            #         #print(acceleration2)
            #     #plt.pause(0.1)


def writeFile(timing, accel, gyro, accelT, gyroT):
    global fileNameIndex
    fileName = 'BicepCurl_RightHand_NotCorrect_HalfDown_' + str(fileNameIndex) + '.csv'
    #fileName = 'ShoulderPress_RightHand_Correct_' + str(fileNameIndex) + '.csv'
    sample_number = accel.shape[1]
    with open(fileName, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["time", "aX", "aY", "aZ", "gX", "gY", "gZ", "aX_T", "aY_T", "aZ_T", "gX_T", "gY_T", "gZ_T"])
        for i in range(0, sample_number):
            writer.writerow([timing[i], accel[0][i], accel[1][i], accel[2][i], gyro[0][i], gyro[1][i], gyro[2][i], accelT[0][i], accelT[1][i], accelT[2][i], gyroT[0][i], gyroT[1][i], gyroT[2][i]])

    fileNameIndex = fileNameIndex + 1
    userInput = input('Finish Logging. Press a key to record a new one.\n')
    print('Going to start recording in 5 seconds')
    time.sleep(int(5))
    print('StartRecording')


if __name__ == "__main__":
    main()
