// Serial WebClient for ESP01
// This sketch get JSON data via serial port from host controller and send
// https POST request to a web server

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

#define MAX_LEN 1532    // make sure it is sufficient for your data

char incomingMsg[MAX_LEN];
uint8_t count = 0;
//String incomingData;
// configure those parameters for your network
//const char *ssid = "TALKTALK4427AC";
//const char *password = "PMARNG9G";
const char *ssid = "DUMAGUS";
const char *password = "192837465";
const char *url = "http://192.168.1.30"; //Home
//const char *url = "http://85.74.248.207"; //Marios

//const char *ssid = "PWW";
//const char *password = "192837465";
//const char *url = "http://192.168.137.1"; //Home


const size_t capacity = 20*JSON_ARRAY_SIZE(3) + 2*JSON_ARRAY_SIZE(10) + JSON_OBJECT_SIZE(8) + 30;
//char json[capacity];
/*
void sendPostRequest(char *json) {

  // send https POST request to server
  HTTPClient https;
  https.begin(url);
  https.addHeader("Content-Type", "application/json");
  int statusCode = https.POST(json);
  // send server response http status code through serial
  char statusAscii[5];
  itoa(statusCode, statusAscii, 10);
  Serial.print(statusAscii);
  Serial.print('\n');

  https.end();
}*/
void sendPostRequest(String &incomingData) {

  // send https POST request to server
  HTTPClient https;
  https.begin(url);
  https.addHeader("Content-Type", "application/json");
  https.addHeader("Authorization", "ED%ygW*2(xY{6*2P");
  int statusCode = https.POST(incomingData);
  digitalWrite(2, LOW);
  // send server response http status code through serial
  //char statusAscii[5];
  //itoa(statusCode, statusAscii, 10);
  //digitalWrite(2, LOW);
  //Serial.flush();
  //Serial.print(statusAscii);
  //Serial.print('\n');
  
  https.end();
}

void setup(void) {
  Serial.begin(115200);
  pinMode(2, OUTPUT);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
  }
  Serial.print("Wifi Ready\n");
}

void loop(void) {
  while (Serial.available() > 0) {
    //StaticJsonDocument<capacity> doc;
    //json = deserializeJson(doc, Serial);
    //char json[capacity];
    //int i = Serial.readBytesUntil('\n', json, capacity);
    String incomingData = Serial.readStringUntil('\n');
    digitalWrite(2, HIGH);
    //Serial.print("Done");
    Serial.print('\n');
    sendPostRequest(incomingData);                     // reset buffer pointer

  }
  /*
    while (Serial.available() > 0) {
      //StaticJsonDocument<capacity> doc;
    char c = Serial.read();
    //char c = Serial.readBytesUntil('\n');
    if (c == '\n') {
      incomingMsg[count] = '\0';         // terminating null byte
      sendPostRequest();
      count = 0;                      // reset buffer pointer
      Serial.print("Going Sleep\n");
      delay(1);                      // for Serial to finish sending
      //ESP.deepSleep(0);
    }
    else {
      if (count < (MAX_LEN - 1)) {
        incomingMsg[count++] = c;
      }
    }
    }*/
}
