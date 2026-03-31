import paho.mqtt.client as mqtt
import time

BROKER="localhost"
TOPIC="hvac/temp"

client=mqtt.Client()

client.connect(BROKER)

temp=20
direction=1

while True:

    client.publish(TOPIC,str(temp))

    print("Publishing temp:",temp)

    temp+=direction*0.3

    if temp>30:
        direction=-1

    if temp<18:
        direction=1

    time.sleep(1)