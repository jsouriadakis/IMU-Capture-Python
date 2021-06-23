#include <Arduino.h>
#include <Arduino_LSM9DS1.h>
#include <ArduinoJson.h>

#define MAX_LEN 50
#define gscale 1

int delayBetweenPoll = 10;
uint8_t count = 0;
char incomingMsg[MAX_LEN];

UART mySerial(digitalPinToPinName(4), digitalPinToPinName(3), NC, NC);

const size_t capacity =40*JSON_ARRAY_SIZE(3) + 2*JSON_ARRAY_SIZE(20) + JSON_OBJECT_SIZE(8); //2 * JSON_ARRAY_SIZE(10) + 20 * JSON_OBJECT_SIZE(3) + JSON_OBJECT_SIZE(8);

void setup() {
  Serial.begin(115200);
  mySerial.begin(115200);
  pinMode(10, INPUT);
  if (!IMU.begin())
  {
    Serial.println("Failed to initialize IMU");
    // stop here if you can't access the IMU:
    while (true);
  }
  // Accelerometer code
  IMU.setAccelFS(3);
  IMU.setAccelODR(5);
  IMU.setAccelOffset(0.001094, -0.001956, -0.024317);
  IMU.setAccelSlope (1.001249, 1.001332, 1.000763);

  // Gyroscope code
  IMU.gyroUnit = RADIANSPERSECOND;
  IMU.setGyroFS(2);
  IMU.setGyroODR(5);
  IMU.setGyroOffset (-0.678192, 0.453033, 0.140472);
  IMU.setGyroSlope (1.199865, 1.147166, 1.138433);


  // Magnetometer code
  IMU.setMagnetFS(0);
  IMU.setMagnetODR(8);
  IMU.setMagnetOffset(13.690186, 18.759766, -9.971924);
  IMU.setMagnetSlope (1.126728, 1.133473, 1.297501);



  Serial.println("Gyro settting ");
  Serial.print("Gyroscope FS= ");    Serial.print(IMU.getGyroFS());
  Serial.print("Gyroscope ODR=");  Serial.println(IMU.getGyroODR());
  Serial.print("Gyro unit=");           Serial.println(IMU.gyroUnit);

  // The slowest ODR determines the sensor rate, Accel and Gyro share their ODR
  float sensorRate = min(IMU.getGyroODR(), IMU.getMagnetODR());
}

void loop() {
  /*
  while (mySerial.available() > 0) {
    char c = mySerial.read();
    if (c == '\n')
    {
        SendData();
    }
  }
  
  // check if the IMU is ready to read:
  while (mySerial.available() > 0) {
    char c = mySerial.read();
    switch (c) {
      case '\r':
        break;
      case '\n':
        SendData();
        count = 0;

        break;
      default:
        if (count < (MAX_LEN - 1)) {
          incomingMsg[count++] = c;
        }
        break;
    }

  }*/
  SendData();
}

void SendData()
{
  float acc[3];
  float gyr[3];
  Serial.println(incomingMsg);
  StaticJsonDocument<1431> doc; //1431
  //DynamicJsonDocument doc(capacity);

  doc["u_id"] = 123;
  doc["d_id"] = 123;
  doc["t"] = millis();
  doc["w"] = 1.1;
  doc["d"] = 1.1;

  JsonArray a = doc.createNestedArray("a");
  JsonArray g = doc.createNestedArray("g");
  for (int i = 0; i < 8; i++)
  {
    if (IMU.accelerationAvailable() &&
        IMU.gyroscopeAvailable())
    {
      // read all 9 DOF of the IMU:
      IMU.readAcceleration(acc[0], acc[1], acc[2]);
      IMU.readGyro(gyr[0], gyr[1], gyr[2]);
      JsonArray a_ = a.createNestedArray();
      JsonArray g_ = g.createNestedArray();
      a_.add(acc[0]);
      a_.add(acc[1]);
      a_.add(acc[2]);
      g_.add(gyr[0]);
      g_.add(gyr[1]);
      g_.add(gyr[2]);
      if (i != 9)
      {
        delay(6);
      }


    }
  }
  doc["t2"] = millis();
  String s1;
  serializeJson(doc, s1);
  /*
  while (mySerial.available() > 0) {
    char c = mySerial.read();
    if (c == '\n')
    {
      break;
    }
  }*/
  while(true)
  {
    int val = digitalRead(10);
    if (val < 1)
    {
      break;
    }
    Serial.println(val);
  }
  
  mySerial.println(s1);
  //Serial.println(s1);
}
