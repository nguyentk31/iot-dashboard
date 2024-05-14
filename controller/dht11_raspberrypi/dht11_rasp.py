from time import sleep
import board
import adafruit_dht
import json
from paho.mqtt import client

## DHT 11
sensor = adafruit_dht.DHT11(board.D4)

## MQTT
broker = 'localhost'
port = 1883
client_id = 'raspberry-pi'
username = 'iot'
password = '123456'

def on_connect(client, userdata, flags, rc, properties):
  if rc == 0:
    print("Connected to MQTT Broker!")
  else:
    print("Failed to connect, return code %d\n", rc)

mqtt_client = client.Client(client_id=client_id, callback_api_version=client.CallbackAPIVersion.VERSION2)
mqtt_client.username_pw_set(username, password)
mqtt_client.connect(broker, port)

mqtt_client.on_connect = on_connect
mqtt_client.loop_start()


## Publish message to mqtt broker
def mqtt_publish(pub_topic, data):
  json_sent = json.dumps(data)
  result = mqtt_client.publish(pub_topic, json_sent)
  status = result[0]
  if status == 0:
    print(f"Send msg to topic {pub_topic}")
  else:
    print(f"Failed to send message to topic {pub_topic}")

if __name__ == '__main__':
  try:
    while True:
      try:
        temperature_c = sensor.temperature
        humidity = sensor.humidity
        print("Temp={0:0.1f}ºC, Humidity={2:0.1f}%".format(temperature_c, humidity))

        mqtt_publish('Sensor', 
          {
            'deviceID': 2,
            'sensorName': 'DHT11-Temperature',
            'sensorValue': temperature_c,
          }
        )

        mqtt_publish('Sensor',
          {
            'deviceID': 2,
            'sensorName': 'DHT11-Humidity',
            'sensorValue': humidity,
          }
        )

      except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        sleep(2)
        continue

      sleep(5)
  except KeyboardInterrupt:
    sensor.exit()
    print('MQTT stopping!')
    mqtt_client.loop_stop()
    print('MQTT stopped!')
    