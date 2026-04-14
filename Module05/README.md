# MODULE 5 - IoT Systems

## Week 1

1) We use various hardware bits and pieces connected with wires. They communicate with each other via MQTT protocol over the air. To do this, we have a Mango router set up that runs the MQTT server. To flash code to our ESPs we use either Arduino IDE or PlatformIO. We did this both over the air and via cable. We also use Node Red to hold some logic and create dashboards based on the MQTT data being sent.

2) Flashing via cable is annoying. We got OTA flashing working but didn't continue to use it that much because it was also painful to set up. Also setting up the network and getting that working was a pain point. Debugging was also quite difficult -- is the problem in code, in serial monitoring, in wiring, bad hardware element, etc.

3) I think the current solution as is will not scale well. And even when we scale it, for example, to 100 devices, then it will be very hard to maintain. Flahing 100 devices one by one. Debugging wiring problems, broken pins/soldering.

More specific problems with scaling:

- Flashing one by one, even with OTA, is annoying. Doesn't alway work.
- Big systems are hard to maintain and might face hardware limitations/bottlenecking when scaling. Several small systems are harder to coordinate and monitor.
- Hard to test, because tasks are distributed. Hard to debug.
- To fix this: something like kubernetes for ESPs where you can manage (batch flash) and monitor all your devices. Detect problems etc.

Management frameworks vs Integration frameworks:

Most general difference.
Device management frameworks -- manage the lifecycle and operation of devices
Integration frameworks -- connect IoT data and services to other systems

Some strong points:
ESPhome -- Seems easy to use and integrate for smart home systems. Free, open source.
Mongoose -- Seems production grade, secure. They claim it's fast and secure.
Node-RED -- Easy to use, visual.
OpenHAB -- Good abstraction, open source.

IoTempower -- cool.

### Task 1

Followed the steps in github. Could pretty easily flash the Wemos within the IoT system. Also got OTA working quite simply. Pictures and screenshots are present.

### Task 2

Followed the steps in github. Introduces the second node. it has a button that can light up the LED on the other node. All this works using Node-RED. Everything went quite smoothly. Pictures are present. Also tested the toggle node.

## Week 2

We made a hotel room where there is a microphone that detects if there is too much noise. Then a LED strip starts flashing and a buzzer goes off to scare the guests. A person at reception can turn it off (node red). 

More info: https://github.com/mattiastamm/IoT-Tamm
