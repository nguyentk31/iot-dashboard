import json
from paho.mqtt import client
import random
from time import sleep

class MQTT_Client:
  def __init__(self, broker, port, client_id, username, password) -> None:
    def on_connect(client, userdata, flags, rc, properties):
      if rc == 0:
        print("Connected to MQTT Broker!")
      else:
        print("Failed to connect, return code %d\n", rc)

    def on_message(client, userdata, msg):
      m_decode = str(msg.payload.decode('utf-8', 'ignore'))
      json_recv = json.loads(m_decode)
      print(f'Received message from {msg.topic} topic')
      print(f'LightID: {json_recv['lightID']} Status: {json_recv['status']}')

    # When init instance, it will connect to broker
    self.client = client.Client(client_id=client_id, callback_api_version=client.CallbackAPIVersion.VERSION2)
    self.client.username_pw_set(username, password)
    self.client.connect(broker, port)

    self.client.on_connect = on_connect
    self.client.on_message = on_message

  # Subcribe function
  def subscribe(self, sub_topic):
    self.client.subscribe(sub_topic)

  # Publish function
  def publish(self, pub_topic, data):
    json_sent = json.dumps(data)
    result = self.client.publish(pub_topic, json_sent)
    status = result[0]
    if status == 0:
      print(f"Device {data['deviceID']} send msg to topic {pub_topic}")
    else:
      print(f"Failed to send message to topic {pub_topic}")

  # Start loop function
  def start(self, is_forever):
    if (is_forever):
      self.client.loop_forever()
    else:
      self.client.loop_start()

  # Stop loop function
  def stop(self):
    self.client.loop_stop()

if __name__ == '__main__':
  broker = 'localhost'
  port = 1883
  client_id = f'python-mqtt-{random.randint(0, 1000)}'
  username = 'iot'
  password = '123456'

  mqtt_client = MQTT_Client(broker, port, client_id, username, password)
  mqtt_client.subscribe('Light')
  mqtt_client.start(False)

  lux = 10000
  tem = 30
  hum = 40


  try:
    while True:
      lux = random.uniform(0 if lux - 500 < 0 else lux - 500, 65535 if lux + 500 > 65535 else lux + 500)
      tem = random.uniform(0 if tem - 5 < 0 else tem - 5, 50 if tem + 5 > 50 else tem + 5)
      hum = random.uniform(20 if hum - 5 < 20 else hum - 5, 90 if hum + 5 > 90 else hum + 5)

      mqtt_client.publish(
        'Sensor', 
        {
          'deviceID': 1,
          'sensorName': 'BH-1750',
          'sensorValue': f"{lux:.2f}",
        }
      )
      print('sleep...zzz')
      sleep(random.randint(0, 5))
      mqtt_client.publish(
        'Sensor', 
        {
          'deviceID': 2,
          'sensorName': 'DHT11-Temperature',
          'sensorValue': f"{tem:.2f}",
        }
      )
      mqtt_client.publish(
        'Sensor', 
        {
          'deviceID': 2,
          'sensorName': 'DHT11-Humidity',
          'sensorValue': f"{hum:.2f}",
        }
      )
      print('sleep...zzz')
      sleep(random.randint(0, 5))
  except KeyboardInterrupt:
    print('MQTT stopping!')
    mqtt_client.stop()
    print('MQTT stopped!')
    