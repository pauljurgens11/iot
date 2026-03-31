import paho.mqtt.client as mqtt
import time

BROKER="localhost"
TOPIC="hvac/ac/set"

ac_state="OFF"

def on_connect(client, userdata, flags, rc):

    print("AC simulator connected")

    client.subscribe(TOPIC)

def on_message(client, userdata, msg):

    global ac_state

    ac_state=msg.payload.decode()

client=mqtt.Client()

client.on_connect=on_connect
client.on_message=on_message

client.connect(BROKER)

client.loop_start()

while True:

    print("AC is:",ac_state)

    time.sleep(1)