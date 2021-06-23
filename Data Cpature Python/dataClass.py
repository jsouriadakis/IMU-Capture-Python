from queue import Queue
import numpy as np
from ahrs.filters import Madgwick
from ahrs.filters import ComplementaryQ
from ahrs.filters import AQUA
from ahrs.common import orientation
from ahrs import Quaternion
from ahrs.utils.plot import plot_sensors
import math
from scipy.spatial.transform import Rotation as Rot
from math import sqrt, atan2, asin, degrees, radians
from scipy.signal import butter, lfilter, freqz, savgol_filter, filtfilt, detrend, find_peaks, medfilt
from scipy.integrate import cumtrapz


sampleRate = 1000 * 10 / 180
gravity = np.array([0, 0, -1])
# gravity = gravity.reshape((3,1))
accelerometerAtRest = 1
gyroscopeAtRest = 0.1
initialQ = [1.0, 0.0, 0.0, 0.0]

class SensorData():

    def __init__(self, index, user_id, device_id, time, time2, weight, distance, acceleration, gyroscope, lastQ):
        self.index = index
        self.user_id = user_id
        self.device_id = device_id
        self.time = time
        self.time2 = time2
        self.weight = weight
        self.distance = distance
        self.acceleration = acceleration
        self.gyroscope = gyroscope
        self.samples = len(acceleration)
        self.sampleRate = 1000 * self.samples / (time2 - time)
        self.Q = np.zeros((self.samples, 4))

        if np.array_equal(lastQ, initialQ):
            self.Q[0] = orientation.acc2q(self.acceleration[0])
        else:
            self.Q[0] = lastQ
        self.transformToWorldFrameNoReset()
        # self.filterData()

    index = 0
    user_id = 0
    device_id = 0
    time = 0
    time2 = 0
    weight = 0
    distance = 0
    acceleration = []
    accelerationT = []
    gyroscope = []
    gyroscopeT = []
    accelMagnitude = []
    rotation = []
    accel = []
    gyro = []
    accelT = []
    gyroT = []
    timing = []
    accelFilteredZ = []
    velocityZ = []
    distanceZ = []
    samples = 0
    sampleRate = 0
    Q = []
    #

    def transformToWorldFrameReset(self):
        self.accel = np.empty([3, self.samples])
        self.gyro = np.empty([3, self.samples])
        self.accelT = np.empty([3, self.samples])
        self.gyroT = np.empty([3, self.samples])
        self.timing = np.empty(self.samples)
        timeStep = (self.time2 - self.time) / self.samples
        madgwickFilter = Madgwick(gyr=np.array(self.gyroscope), acc=np.array(self.acceleration), frequency=self.sampleRate, beta=0.615)
        rotation = madgwickFilter.Q
        for i in range(0, self.samples):
            q = Quaternion(rotation[i])
            q2 = Quaternion(q.inverse)
            R = q.to_DCM()
            R_T = q2.to_DCM()
            newGrav = gravity @ R

            self.accel[0][i] = self.acceleration[i][0]
            self.accel[1][i] = self.acceleration[i][1]
            self.accel[2][i] = self.acceleration[i][2]
            # print("{:.4f}".format(self.accel[0][i]), "{:.4f}".format(self.accel[1][i]),"{:.4f}".format(self.accel[2][i]))
            self.gyro[0][i] = self.gyroscope[i][0]
            self.gyro[1][i] = self.gyroscope[i][1]
            self.gyro[2][i] = self.gyroscope[i][2]

            self.acceleration[i][0] = self.acceleration[i][0] + newGrav[0]
            self.acceleration[i][1] = self.acceleration[i][1] + newGrav[1]
            self.acceleration[i][2] = self.acceleration[i][2] + newGrav[2]

            self.acceleration[i] = self.acceleration[i] @ R_T
            self.gyroscope[i] = self.gyroscope[i] @ R_T

            self.accelT[0][i] = self.acceleration[i][0]
            self.accelT[1][i] = self.acceleration[i][1]
            self.accelT[2][i] = self.acceleration[i][2]
            print("{:.4f}".format(self.accelT[0][i]), "{:.4f}".format(self.accelT[1][i]),"{:.4f}".format(self.accelT[2][i]))
            self.gyroT[0][i] = self.gyroscope[i][0]
            self.gyroT[1][i] = self.gyroscope[i][1]
            self.gyroT[2][i] = self.gyroscope[i][2]
            self.timing[i] = self.time + i * timeStep

    def transformToWorldFrameSoftReset(self):
        self.accel = np.empty([3, self.samples])
        self.gyro = np.empty([3, self.samples])
        self.accelT = np.empty([3, self.samples])
        self.gyroT = np.empty([3, self.samples])
        self.timing = np.empty(self.samples)
        timeStep = (self.time2 - self.time)/self.samples

        madgwickFilter2 = Madgwick(frequency=self.sampleRate, beta=0.3)
        for i in range(0, self.samples):
            #madgwickFilter2.Dt = 1.0 / self.sampleRate
            if i < self.samples - 1:
                self.Q[i+1] = madgwickFilter2.updateIMU(self.Q[i], gyr=self.gyroscope[i+1], acc=self.acceleration[i+1])

            if i < self.samples - 3:
                magnitude1 = sqrt(
                    self.acceleration[i + 1][0] * self.acceleration[i + 1][0] + self.acceleration[i + 1][1] *
                    self.acceleration[i + 1][
                        1] + self.acceleration[i + 1][2] * self.acceleration[i + 1][2])
                magnitude2 = sqrt(
                    self.acceleration[i + 2][0] * self.acceleration[i + 2][0] + self.acceleration[i + 2][1] *
                    self.acceleration[i + 2][
                        1] + self.acceleration[i + 2][2] * self.acceleration[i + 2][2])
                magnitude3 = sqrt(
                    self.acceleration[i + 3][0] * self.acceleration[i + 3][0] + self.acceleration[i + 3][1] *
                    self.acceleration[i + 3][
                        1] + self.acceleration[i + 3][2] * self.acceleration[i + 3][2])
                magnitude = (magnitude1 + magnitude2 + magnitude3)/3
                if magnitude > 0.98 and magnitude < 1.02:
                    self.Q[i + 1] = orientation.acc2q(self.acceleration[i + 1])

            q = Quaternion(self.Q[i])
            q2 = Quaternion(q.inverse)
            R = q.to_DCM()
            R_T = q2.to_DCM()
            newGrav = gravity @ R

            self.accel[0][i] = self.acceleration[i][0]
            self.accel[1][i] = self.acceleration[i][1]
            self.accel[2][i] = self.acceleration[i][2]
            # print("{:.4f}".format(self.accel[0][i]), "{:.4f}".format(self.accel[1][i]),"{:.4f}".format(self.accel[2][i]))
            self.gyro[0][i] = self.gyroscope[i][0]
            self.gyro[1][i] = self.gyroscope[i][1]
            self.gyro[2][i] = self.gyroscope[i][2]

            self.acceleration[i][0] = self.acceleration[i][0] + newGrav[0]
            self.acceleration[i][1] = self.acceleration[i][1] + newGrav[1]
            self.acceleration[i][2] = self.acceleration[i][2] + newGrav[2]

            self.acceleration[i] = self.acceleration[i] @ R_T
            self.gyroscope[i] = self.gyroscope[i] @ R_T

            self.accelT[0][i] = self.acceleration[i][0]
            self.accelT[1][i] = self.acceleration[i][1]
            self.accelT[2][i] = self.acceleration[i][2]
            print("{:.4f}".format(self.accelT[0][i]), "{:.4f}".format(self.accelT[1][i]), "{:.4f}".format(self.accelT[2][i]))
            self.gyroT[0][i] = self.gyroscope[i][0]
            self.gyroT[1][i] = self.gyroscope[i][1]
            self.gyroT[2][i] = self.gyroscope[i][2]

            self.timing[i] = self.time + i * timeStep

    def transformToWorldFrameNoReset(self):
        self.accel = np.empty([3, self.samples])
        self.gyro = np.empty([3, self.samples])
        self.accelT = np.empty([3, self.samples])
        self.gyroT = np.empty([3, self.samples])
        self.timing = np.empty(self.samples)
        timeStep = (self.time2 - self.time)/self.samples

        madgwickFilter2 = Madgwick(frequency=self.sampleRate/4, beta=0.1)
        for i in range(0, self.samples):
            #madgwickFilter2.Dt = 1.0 / self.sampleRate
            if i < self.samples - 1:
                self.Q[i+1] = madgwickFilter2.updateIMU(self.Q[i], gyr=self.gyroscope[i+1], acc=self.acceleration[i+1])
                magnitude = sqrt(
                    self.acceleration[i+1][0] * self.acceleration[i+1][0] + self.acceleration[i+1][1] * self.acceleration[i+1][
                        1] + self.acceleration[i+1][2] * self.acceleration[i+1][2])
                #if magnitude > 0.97 and magnitude < 1.03:
                    #self.Q[i+1] = orientation.acc2q(self.acceleration[i+1])

            q = Quaternion(self.Q[i])
            q2 = Quaternion(q.inverse)
            R = q.to_DCM()
            R_T = q2.to_DCM()
            newGrav = gravity @ R

            self.accel[0][i] = self.acceleration[i][0]
            self.accel[1][i] = self.acceleration[i][1]
            self.accel[2][i] = self.acceleration[i][2]
            # print("{:.4f}".format(self.accel[0][i]), "{:.4f}".format(self.accel[1][i]),"{:.4f}".format(self.accel[2][i]))
            self.gyro[0][i] = self.gyroscope[i][0]
            self.gyro[1][i] = self.gyroscope[i][1]
            self.gyro[2][i] = self.gyroscope[i][2]

            self.acceleration[i][0] = self.acceleration[i][0] + newGrav[0]
            self.acceleration[i][1] = self.acceleration[i][1] + newGrav[1]
            self.acceleration[i][2] = self.acceleration[i][2] + newGrav[2]

            self.acceleration[i] = self.acceleration[i] @ R_T
            self.gyroscope[i] = self.gyroscope[i] @ R_T

            self.accelT[0][i] = self.acceleration[i][0]
            self.accelT[1][i] = self.acceleration[i][1]
            self.accelT[2][i] = self.acceleration[i][2]
            #print("{:.4f}".format(self.accelT[0][i]), "{:.4f}".format(self.accelT[1][i]), "{:.4f}".format(self.accelT[2][i]))
            self.gyroT[0][i] = self.gyroscope[i][0]
            self.gyroT[1][i] = self.gyroscope[i][1]
            self.gyroT[2][i] = self.gyroscope[i][2]

            self.timing[i] = self.time + i * timeStep

    def transformToWorldFrameNoReset2(self):
        self.accel = np.empty([3, self.samples])
        self.gyro = np.empty([3, self.samples])
        self.accelT = np.empty([3, self.samples])
        self.gyroT = np.empty([3, self.samples])
        self.timing = np.empty(self.samples)
        timeStep = (self.time2 - self.time)/self.samples

        madgwickFilter2 = Madgwick(frequency=self.sampleRate/8, beta=0.5)
        for i in range(0, self.samples):
            #madgwickFilter2.Dt = 1.0 / self.sampleRate
            if i < self.samples - 1:
                self.Q[i+1] = madgwickFilter2.updateIMU(self.Q[i], gyr=self.gyroscope[i+1], acc=self.acceleration[i+1])
                magnitude = sqrt(
                    self.acceleration[i+1][0] * self.acceleration[i+1][0] + self.acceleration[i+1][1] * self.acceleration[i+1][
                        1] + self.acceleration[i+1][2] * self.acceleration[i+1][2])
                #if magnitude > 0.97 and magnitude < 1.03:
                    #self.Q[i+1] = orientation.acc2q(self.acceleration[i+1])

            q = Quaternion(self.Q[i])
            q2 = Quaternion(q.inverse)
            R = q.to_DCM()
            R_T = q2.to_DCM()
            newGrav = gravity @ R

            self.accel[0][i] = self.acceleration[i][0]
            self.accel[1][i] = self.acceleration[i][1]
            self.accel[2][i] = self.acceleration[i][2]
            # print("{:.4f}".format(self.accel[0][i]), "{:.4f}".format(self.accel[1][i]),"{:.4f}".format(self.accel[2][i]))
            self.gyro[0][i] = self.gyroscope[i][0]
            self.gyro[1][i] = self.gyroscope[i][1]
            self.gyro[2][i] = self.gyroscope[i][2]

            self.acceleration[i][0] = self.acceleration[i][0] + newGrav[0]
            self.acceleration[i][1] = self.acceleration[i][1] + newGrav[1]
            self.acceleration[i][2] = self.acceleration[i][2] + newGrav[2]

            self.acceleration[i] = self.acceleration[i] @ R_T
            self.gyroscope[i] = self.gyroscope[i] @ R_T

            self.accelT[0][i] = self.acceleration[i][0]
            self.accelT[1][i] = self.acceleration[i][1]
            self.accelT[2][i] = self.acceleration[i][2]
            #print("{:.4f}".format(self.accelT[0][i]), "{:.4f}".format(self.accelT[1][i]), "{:.4f}".format(self.accelT[2][i]))
            self.gyroT[0][i] = self.gyroscope[i][0]
            self.gyroT[1][i] = self.gyroscope[i][1]
            self.gyroT[2][i] = self.gyroscope[i][2]

            self.timing[i] = self.time + i * timeStep
    def returnLastQ(self):
        return self.Q[-1]

    def returnAccGyroTime(self):
        return self.accel, self.accelT, self.gyro, self.gyroT, self.timing


    def returnAccAndGyro2(self):
        accel = np.empty([3, len(self.acceleration)])
        gyro = np.empty([3, len(self.acceleration)])
        for i in range(0, len(self.acceleration)):
            accel[0][i] = self.acceleration[i][0]
            accel[1][i] = self.acceleration[i][1]
            accel[2][i] = self.acceleration[i][2]

            gyro[0][i] = self.gyroscope[i][0]
            gyro[1][i] = self.gyroscope[i][1]
            gyro[2][i] = self.gyroscope[i][2]

        return accel, gyro

    def accelerationMagnitude(self):
        return self.accelMagnitude

    def returnQuaternion(self):
        return self.rotation

    def filterData(self):
        order = 1
        # fs = 20  # sample rate, Hz
        fc = 1.5
        b, a = butter(N=order, Wn=fc / (0.5 * self.sampleRate), btype='low', analog=False)
        d, c = butter(N=order, Wn=fc / (0.5 * self.sampleRate), btype='high', analog=False)

        z_filtered = y = lfilter(b, a, self.accel[2])
        z_filtered = y = medfilt(self.accel[2])
        # print(self.accel[2])
        # z_filtered = y = lfilter(b, a, y)
        # z_filtered = savgol_filter(self.accel[2], 5, 3)
        self.accelFilteredZ = z_filtered
        vel = cumtrapz(z_filtered)
        # vel_detrended = detrend(vel)
        vel_filtered = lfilter(d, c, vel)
        self.velocityZ = vel_filtered

        dist = cumtrapz(vel_filtered)
        dist_filtered = lfilter(d, c, dist)
        dist_filtered = dist_filtered - dist_filtered.mean()
        # dist_detrended = detrend(dist, type='linear')
        self.distanceZ = dist_filtered

    def returnFilteredAccelVelDist(self):
        return self.accelFilteredZ, self.velocityZ, self.distanceZ


COEFFICIENTS_LOW_0_HZ = {
    "alpha": [1, -1.979133761292768, 0.979521463540373],
    "beta": [0.000086384997973502, 0.000172769995947004, 0.000086384997973502]
}

COEFFICIENTS_LOW_5_HZ = {
    "alpha": [1, -1.80898117793047, 0.827224480562408],
    "beta": [0.095465967120306, -0.172688631608676, 0.095465967120306]
}

COEFFICIENTS_HIGH_1_HZ = {
    "alpha": [1, -1.905384612118461, 0.910092542787947],
    "beta": [0.953986986993339, -1.907503180919730, 0.953986986993339]
}


class Filter:
    filtered_data = []

    def low_0_hz(self, data):
        self.filter(data, COEFFICIENTS_LOW_0_HZ)

    def low_5_hz(self, data):
        self.filter(data, COEFFICIENTS_LOW_5_HZ)

    def high_1_hz(self, data):
        self.filter(data, COEFFICIENTS_HIGH_1_HZ)

    def filter(self, data, coefficients):
        if len(self.filtered_data.shape[0]) == 0:
            temp = np.zeros([np.shape(data)[0], 1])
            self.filtered_data.append(temp)
            self.filtered_data.append(temp)

        # for i in range(2, len(data) - 1):
        #     temp[0][i] = (coefficients['alpha'][0] *
        #             (data[:, i] * coefficients['beta'][0] +
        #              data[:, i - 1] * coefficients['beta'][1] +
        #              data[:, i - 2] * coefficients['beta'][2] -
        #              self.filtered_data[:, i - 1] * coefficients['alpha'][1] -
        #              self.filtered_data[:, i - 2] * coefficients['alpha'][2]))
        #     temp[1] =
        #     temp[2] =
        #     print(temp)
        #     self.filtered_data.append(temp)
        #     if len(self.filtered_data) > len(data):
        #         self.filtered_data.pop(0)

        return self.filtered_data
