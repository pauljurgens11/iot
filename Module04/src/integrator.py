import paho.mqtt.client as mqtt

BROKER="localhost"

TEMP_TOPIC="hvac/temp"
AC_SET_TOPIC="hvac/ac/set"

AC_ON_TEMP=25
AC_OFF_TEMP=22

ac_state=False

def on_connect(client, userdata, flags, rc):
    print("Integrator connected")
    client.subscribe(TEMP_TOPIC)

def on_message(client, userdata, msg):
    global ac_state

    temp=float(msg.payload.decode())

    print("Temperature:",temp)

    if temp > AC_ON_TEMP and not ac_state:

        client.publish(AC_SET_TOPIC,"ON")
        ac_state=True

        print("AC turned ON")

    elif temp < AC_OFF_TEMP and ac_state:

        client.publish(AC_SET_TOPIC,"OFF")
        ac_state=False

        print("AC turned OFF")

client=mqtt.Client()

client.on_connect=on_connect
client.on_message=on_message

client.connect(BROKER)

client.loop_forever()