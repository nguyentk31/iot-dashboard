// khai báo thư viện
#include <BH1750.h>
#include <Wire.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// BH-1750 (SCL, SDA) (D1, D2)
BH1750 lightMeter;

// LED
short leds_pin[2] = {D6, D7};

// Thông tin WIFI AP
#define ssid "UiTiOt-E3.1"
#define password "UiTiOtAP"

#define mqtt_cient_id "wemos"
#define mqtt_server "172.31.10.18"
#define mqtt_port 1883
#define mqtt_user "iot"
#define mqtt_pwd "123456"
#define mqtt_topic_light "Light"
#define mqtt_topic_sensor "Sensor"

WiFiClient WIFI_CLIENT;
PubSubClient client(WIFI_CLIENT);

// Hàm call back để nhận dữ liệu
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  String payload_str = String(( char *) payload);
  if (strcmp(topic, "Light") == 0) {
    Serial.println("Light topic");
    StaticJsonDocument<2048> msg;
    deserializeJson(msg, payload_str);
    action(msg["lightID"], msg["status"]);
  }
}

void action(int lightID, int status) {
  digitalWrite(leds_pin[lightID], status);
}

// Hàm kết nối wifi
void setup_wifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Trying to connect to WIFI AP.");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  for (int i = 0; i < 2; i++) {
    pinMode(leds_pin[i], OUTPUT);
  }

  Serial.begin(9600);

  Wire.begin();
  lightMeter.begin();

  setup_wifi();
  // Subscribe to the topic where our web page is publishing messages
  client.setServer(mqtt_server, mqtt_port); 
  // Set the message received callback
  client.setCallback(callback);
}

// Hàm reconnect thực hiện kết nối lại khi mất kết nối với MQTT Broker
void reconnect() {
  // Chờ tới khi kết nối
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Thực hiện kết nối với mqtt user và pass
    if (client.connect(mqtt_cient_id, mqtt_user, mqtt_pwd)) {
      Serial.println("connected");
      // ... và nhận lại thông tin này
      client.subscribe(mqtt_topic_light);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Đợi 5s
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }

  // Read light level
  float lux = lightMeter.readLightLevel();
  Serial.print("Lux: ");
  Serial.println(lux);

  String msg;
  StaticJsonDocument<2048> body;
  body["deviceID"] = 1;
  body["sensorName"] = "BH-1750";
  body["sensorValue"] = round(lux * 10) / 10.0;
  serializeJson(body, msg); 
  Serial.println((char*)msg.c_str());
  Serial.println(client.publish(mqtt_topic_sensor, (char*)msg.c_str()));

  client.loop();
  delay(2000);
}

