# MODULE 4 - EMBEDDED PROGRAMMING AND DEPLOYING NODES

## Week 1

Goal to test some errors and faults. C++ language specifics.

### Task 1

Broken code:

This hits a nullpointer error when receiving a message.

```
/*
 Basic ESP8266 MQTT example
 This sketch demonstrates the capabilities of the pubsub library in combination
 with the ESP8266 board/library.
 It connects to an MQTT server then:
  - publishes "hello world" to the topic "outTopic" every two seconds
  - subscribes to the topic "inTopic", printing out any messages
    it receives. NB - it assumes the received payloads are strings not binary
  - If the first character of the topic "inTopic" is an 1, switch ON the ESP Led,
    else switch it off
 It will reconnect to the server if the connection is lost using a blocking
 reconnect function. See the 'mqtt_reconnect_nonblocking' example for how to
 achieve the same result without blocking the main loop.
 To install the ESP8266 board, (using Arduino 1.6.4+):
  - Add the following 3rd party board manager under "File -> Preferences -> Additional Boards Manager URLs":
       http://arduino.esp8266.com/stable/package_esp8266com_index.json
  - Open the "Tools -> Board -> Board Manager" and click install for the ESP8266"
  - Select your ESP8266 in "Tools -> Board"
*/

#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Update these with values suitable for your network.

const char* ssid = "IOT11";
const char* password = "iotempire";
const char* mqtt_server = "192.168.1.1";

char* super_message;

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE	(50)
char msg[MSG_BUFFER_SIZE];
int value = 0;

void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  // Let's print something special here
  Serial.println("Something special coming up...");
  Serial.print("The following:");
  // update message
  super_message[0] = 'A';
  Serial.println(super_message);


  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

  // Switch on the LED if an 1 was received as first character
  if ((char)payload[0] == '1') {
    digitalWrite(BUILTIN_LED, LOW);   // Turn the LED on (Note that LOW is the voltage level
    // but actually the LED is on; this is because
    // it is active low on the ESP-01)
  } else {
    digitalWrite(BUILTIN_LED, HIGH);  // Turn the LED off by making the voltage HIGH
  }

}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish("outTopic", "hello world");
      // ... and resubscribe
      client.subscribe("inTopic");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  pinMode(BUILTIN_LED, OUTPUT);     // Initialize the BUILTIN_LED pin as an output
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 2000) {
    lastMsg = now;
    ++value;
    snprintf (msg, MSG_BUFFER_SIZE, "hello world #%ld", value);
    Serial.print("Publish message: ");
    Serial.println(msg);
    client.publish("outTopic", msg);
  }
}
```

To fix the error, we instead do:

```
char super_message[10];
```

This actually ensures a real buffer exists and pointer isn't just some random memory address.

### Task 2

Added this to our code to the right places:

```
int new_value = 10;

  --new_value; // instead of ++
  snprintf (msg, MSG_BUFFER_SIZE, "hello world #%ld - division %ld",
     new_value, 1000 / new_value);
```

Got an error on the 10th iteration and no more errors after that. Meaning that the error was as expected. To fix it, we just avoid dividing by 0. For example, do an if check in the code. Pretty simple.

### Task 3

We added the new message function and called it in our loop. Then we started getting OOM errors just as expected.

```
void message() {
   char* msg = new char[512]; // Allocate space
   sprintf(msg, "Hello at %ld.", millis());
  
   static String extend_msg;
   extend_msg += msg;
   extend_msg += "And more";
  
   // Publish without freeing memory
   client.publish("test/output", extend_msg.c_str());
}
```

To fix this we can do this:

```
   extend_msg = msg;          // overwrite instead of growing forever

   delete[] msg;   // FIX: free memory
```

### Task 4

An interrupt is like an emergency button the CPU reacts to immediately.

When the interrupt runs:
- normal program pauses
- WiFi pauses
- timers pause
- other interrupts pause

So the interrupt must finish very fast. So the CPU gets stuck waiting while everything else is frozen → system crashes.

### Task 5

Code that we used to get it working:

```
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>

#ifndef STASSID
#define STASSID "IOT11"
#define STAPSK "iotempire"
#endif

const char* ssid = STASSID;
const char* password = STAPSK;
const char* hostname = "ulno-otatest";

void setup() {
  Serial.begin(115200);
  Serial.println("Booting");
  WiFi.mode(WIFI_STA);
  WiFi.setHostname(hostname);
  WiFi.begin(ssid, password);
  while (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.println("Connection Failed! Rebooting...");
    delay(5000);
    ESP.restart();
  }

  // Port defaults to 8266
  // ArduinoOTA.setPort(8266);

  // Hostname defaults to esp8266-[ChipID]
  ArduinoOTA.setHostname(hostname);

  // No authentication by default
  // ArduinoOTA.setPassword("admin");
  ArduinoOTA.setPassword("iotempower");

  // Password can be set with it's md5 value as well
  // MD5(admin) = 21232f297a57a5a743894a0e4a801fc3
  // ArduinoOTA.setPasswordHash("21232f297a57a5a743894a0e4a801fc3");

  ArduinoOTA.onStart([]() {
    String type;
    if (ArduinoOTA.getCommand() == U_FLASH) {
      type = "sketch";
    } else {  // U_FS
      type = "filesystem";
    }

    // NOTE: if updating FS this would be the place to unmount FS using FS.end()
    Serial.println("Start updating " + type);
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) {
      Serial.println("Auth Failed");
    } else if (error == OTA_BEGIN_ERROR) {
      Serial.println("Begin Failed");
    } else if (error == OTA_CONNECT_ERROR) {
      Serial.println("Connect Failed");
    } else if (error == OTA_RECEIVE_ERROR) {
      Serial.println("Receive Failed");
    } else if (error == OTA_END_ERROR) {
      Serial.println("End Failed");
    }
  });
  ArduinoOTA.begin();
  Serial.println("Ready");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  ArduinoOTA.handle();
}
```

We could flash code now OTA.

### Task 6

We got it working with this code. Used GPT to help us generate it. I have video on my phone but making GIFs is difficult so I can show on phone.

```
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoOTA.h>
#include <ESP8266mDNS.h>

const char* ssid = "IOT11";
const char* password = "iotempire";
const char* mqtt_server = "192.168.1.1";
const char* hostname = "ulno-otatest";

WiFiClient espClient;
PubSubClient client(espClient);

const int ledPin = D5;

bool flashing = false;
unsigned long startTime = 0;

void callback(char* topic, byte* payload, unsigned int length) {

  String message;

  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  if (String(topic) == "alarm") {

    if (message == "on") {
      flashing = true;
      startTime = millis();
    }

    if (message == "off") {
      flashing = false;
      analogWrite(ledPin,0);
    }
  }
}

void reconnect() {

  while (!client.connected()) {

    if (client.connect(hostname)) {

      client.subscribe("alarm");

    } else {

      delay(2000);

    }
  }
}

void setup() {

  Serial.begin(115200);

  pinMode(ledPin, OUTPUT);

  WiFi.mode(WIFI_STA);
  WiFi.setHostname(hostname);
  WiFi.begin(ssid,password);

  while(WiFi.status()!=WL_CONNECTED) {
    delay(500);
  }

  client.setServer(mqtt_server,1883);
  client.setCallback(callback);

  ArduinoOTA.setHostname(hostname);
  ArduinoOTA.setPassword("iotempower");

  ArduinoOTA.begin();
}

void loop() {

  ArduinoOTA.handle();

  if(!client.connected()) {
    reconnect();
  }

  client.loop();

  if(flashing) {

    unsigned long currentTime = millis();

    if(currentTime - startTime < 30000) {

      int brightness =
      (sin((currentTime - startTime)/1000.0 * PI) * 127.5) + 127.5;

      analogWrite(ledPin,brightness);

    }
    else {

      flashing = false;
      analogWrite(ledPin,0);

    }
  }
}
```

### Task 7

Part 1 – Research

How many hardware serial (UART) interfaces are available on:

ESP8266 / Wemos D1 Mini - 2 interfaces
ESP32 / MH-ET LIVE ESP32 MiniKit - 3 interfaces

Which Arduino objects (Serial, Serial1, Serial2) correspond to them, and which GPIO pins are typically used?

UART0 Serial GPIO1 (TX) GPIO3 (RX) Full TX/RX, used for USB
UART1 Serial1 GPIO2 (TX) ❌ none TX only

UART0 Serial GPIO1 GPIO3 USB programming/debug
UART1 Serial1 GPIO10 GPIO9 Can be remapped
UART2 Serial2 GPIO17 GPIO16 Can be remapped

What is the difference between hardware serial and software serial communication?
Which one is generally more stable, and when might software serial be needed?

Hardware serial uses dedicated UART hardware inside the microcontroller. Software serial emulates UART using normal GPIO pins and CPU timing.

Hardware serial is always more stable.

Software serial is only used when:
	•	No free hardware UART exists
	•	Additional serial device needed
	•	Low speed device (GPS, sensors)
	•	Debugging secondary device


Part 2

Code for node A:

```
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SoftwareSerial.h>

const char* ssid = "IOT11";
const char* password = "iotempire";
const char* mqtt_server = "192.168.1.1";
const char* mqtt_topic = "prison/security";

// SoftwareSerial: RX, TX
SoftwareSerial linkSerial(D6, D5);

WiFiClient espClient;
PubSubClient client(espClient);

void setupWifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("Wi-Fi connected");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += static_cast<char>(payload[i]);
  }

  Serial.print("MQTT message on topic ");
  Serial.print(topic);
  Serial.print(": ");
  Serial.println(message);

  if (String(topic) == mqtt_topic) {
    linkSerial.println(message);
    Serial.println("Forwarded over serial");
  }
}

void reconnectMqtt() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    String clientId = "NodeA-";
    clientId += String(ESP.getChipId(), HEX);

    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.subscribe(mqtt_topic);
      Serial.print("Subscribed to: ");
      Serial.println(mqtt_topic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 2 seconds");
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  linkSerial.begin(9600);

  Serial.println();
  Serial.println("Node A starting...");

  setupWifi();

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnectMqtt();
  }
  client.loop();
}
```

Code for node B:

```
#include <SoftwareSerial.h>

SoftwareSerial linkSerial(D5, D6);

String incomingText = "";

void receiveMessage();
void processMessage(String msg);

void setup() {
  Serial.begin(115200);
  linkSerial.begin(9600);
  pinMode(D5, INPUT_PULLUP);

  Serial.println("Node B ready");
}

void loop() {
  receiveMessage();
}

void receiveMessage() {
  while (linkSerial.available()) {
    char c = linkSerial.read();

    if (c == '\n') {
      processMessage(incomingText);
      incomingText = "";
    }
    else if (isPrintable(c) || c == ' ') {
      incomingText += c;
    }
  }
}

void processMessage(String msg) {
  msg.trim();

  if (msg.length() == 0) return;

  Serial.print("Received: ");
  Serial.println(msg);
}
```

Node A TX  -> Node B RX (we used software serial D5 and D6 actually on both)
Node A RX  -> Node B TX
Node A GND -> Node B GND

We send a message with MQTT to node a, node a forwards it to node b through the serial cable. Node b has no WIFI connection.

### Task 8

This draws the message on screen. We got it working.

```
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoOTA.h>
#include <Wire.h>
#include <U8g2lib.h>

const char* ssid = "IOT11";
const char* password = "iotempire";
const char* mqtt_server = "192.168.1.1";

const char* hostname = "esp32-alarm-2";

WiFiClient espClient;
PubSubClient client(espClient);

String alarmMessage = "Waiting hi...";

U8G2_SSD1306_64X48_ER_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);

void callback(char* topic, byte* payload, unsigned int length) {

  alarmMessage = "";

  for(unsigned int i=0;i<length;i++) {
    alarmMessage += (char)payload[i];
  }

  Serial.println("MQTT message:");
  Serial.println(alarmMessage);
}

void reconnect() {

  while(!client.connected()) {

    Serial.println("Connecting MQTT...");

    if(client.connect(hostname)) {

      client.subscribe("prison/alarm");

      Serial.println("MQTT connected");

    } else {

      delay(2000);

    }
  }
}

void setup() {

  Serial.begin(115200);
  Serial.print("hiiiiiii");

  Wire.begin(21,22);

  u8g2.begin();

  WiFi.mode(WIFI_STA);
  WiFi.setHostname(hostname);
  WiFi.begin(ssid,password);

  Serial.print("Connecting WiFi");

  while(WiFi.status()!=WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("Connected");

  client.setServer(mqtt_server,1883);
  client.setCallback(callback);

  ArduinoOTA.setHostname(hostname);
  ArduinoOTA.setPassword("iotempower");

  ArduinoOTA.begin();

}

void loop() {

  ArduinoOTA.handle();

  if(!client.connected()) {
    reconnect();
  }

  client.loop();

  u8g2.clearBuffer();

  u8g2.setFont(u8g2_font_5x7_tr);

  u8g2.drawStr(0,10,"Security:");

  u8g2.drawStr(0,25,alarmMessage.c_str());

  u8g2.sendBuffer();

  delay(200);
}
```

### Task 9

Got it working. Pictures attached. Code:

```
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <FastLED.h>
#include <Wire.h>
#include <U8g2lib.h>

#define LED_PIN 25
#define NUM_LEDS 30

const char* ssid = "IOT11";
const char* password = "iotempire";
const char* mqtt_server = "192.168.1.1";

WiFiClient espClient;
PubSubClient client(espClient);

CRGB leds[NUM_LEDS];

String alarmState="all_clear";

U8G2_SSD1306_64X48_ER_F_HW_I2C u8g2(U8G2_R0,U8X8_PIN_NONE);

void callback(char* topic, byte* payload, unsigned int length){

  alarmState="";

  for(int i=0;i<length;i++){
    alarmState += (char)payload[i];
  }

  Serial.println(alarmState);

}

void reconnect(){

  while(!client.connected()){

    if(client.connect("esp32alarm")){
      client.subscribe("prison/alarm");
    }
    else{
      delay(2000);
    }
  }
}

void setup(){

  Serial.begin(115200);

  Wire.begin(21,22);

  u8g2.begin();

  FastLED.addLeds<WS2812,LED_PIN,GRB>(leds,NUM_LEDS);

  WiFi.begin(ssid,password);

  while(WiFi.status()!=WL_CONNECTED){
    delay(500);
  }

  client.setServer(mqtt_server,1883);
  client.setCallback(callback);
}

void loop(){

  if(!client.connected()){
    reconnect();
  }

  client.loop();

  // LED behaviour
  if(alarmState=="all_clear"){

    for(int i=0;i<NUM_LEDS;i++){
      leds[i]=CRGB::Green;
    }

    FastLED.show();
  }

  if(alarmState=="possible_threat"){

    static int b=0;
    static int dir=5;

    b+=dir;

    if(b>255 || b<0)
      dir=-dir;

    for(int i=0;i<NUM_LEDS;i++){
      leds[i]=CRGB(b,0,0);
    }

    FastLED.show();
  }

  if(alarmState=="lockdown"){

    static bool state=false;

    state=!state;

    for(int i=0;i<NUM_LEDS;i++){
      leds[i]= state ? CRGB::Red : CRGB::Black;
    }

    FastLED.show();

    delay(200);
  }

  // OLED display
  u8g2.clearBuffer();

  u8g2.setFont(u8g2_font_5x7_tr);

  u8g2.drawStr(0,10,"Security:");

  u8g2.drawStr(0,30,alarmState.c_str());

  u8g2.sendBuffer();

  delay(50);
}
```

## Week 2 (actually week 3)

### MQTT

MQTT is quite a nice tool/protocol to use in IoT because it enables us the define and exchange various messages between devices. This enables standardised over the air communication.

Actors can publish/subscribe to topics and the developer can manage the details. Very nice.

For example, we can use our phone to send some data to a IoT device over WiFi using MQTT.

Simulating and emulating is good for prototyping. Easy to tie stuff together with MQTT.

### Task 1

We implemented the integrator, ac simulator, and temperature sensor simulator in code. They can all be found [here](./src).

We tried to go the simplest route to quickly reach a state which enables testing the code and communication.

The temperature simulator starts sending the temperature over MQTT and slowly raises it from 18 degrees to 30 degrees and then back down to 18 degrees in a loop. The integrator listens for the temperature, and if it exceeds a certain threshold (22 degrees), it sends a "turn on" message to the AC simulator (or "turn off" depending on the direction). The AC simulator waits for updates and changes its state accordingly. Overall very simple.

Also, we ran the MQTT broker on localhost to keep things simple. And used ChatGPT model 5.2 to help us generate the code.

### Task 1 continued

I connected the parts together initially. I used 2 separate Wemos ESPs. One detects and sends temperature, other listens and switches the solenoid lock on/off (AC). Got them working. Pictures are uploaded.

Code:

```
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define RELAY_PIN D1

const char* ssid = "IOT11";
const char* password = "iotempire";
const char* mqtt_server = "192.168.1.1";

WiFiClient espClient;
PubSubClient client(espClient);

bool acState=false;

unsigned long lastStatus=0;
unsigned long acStartTime=0;

void setupWifi()
{
 WiFi.begin(ssid,password);

 while(WiFi.status()!=WL_CONNECTED)
 {
  delay(500);
 }
}

void publishStatus()
{
 if(acState)
  client.publish("hvac/ac/status","ON");
 else
  client.publish("hvac/ac/status","OFF");
}

void callback(char* topic, byte* payload, unsigned int length)
{
 String msg="";

 for(int i=0;i<length;i++)
  msg+=(char)payload[i];

 if(msg=="ON")
 {
  digitalWrite(RELAY_PIN,HIGH);   // active LOW relay

  acState=true;

  acStartTime=millis();

  publishStatus();
 }

 if(msg=="OFF")
 {
  digitalWrite(RELAY_PIN,LOW);

  acState=false;

  publishStatus();
 }
}

void reconnect()
{
 while(!client.connected())
 {
  client.connect("AC_node");

  client.subscribe("hvac/ac/set");

  delay(500);
 }
}

void setup()
{
 Serial.begin(115200);

 pinMode(RELAY_PIN,OUTPUT);

 digitalWrite(RELAY_PIN,LOW);

 setupWifi();

 client.setServer(mqtt_server,1883);

 client.setCallback(callback);
}

void loop()
{
 if(!client.connected())
  reconnect();

 client.loop();

 unsigned long now=millis();

 // safety timeout 30s
 if(acState && now-acStartTime>10000)
 {
  digitalWrite(RELAY_PIN,LOW);

  acState=false;

  publishStatus();
 }

 // publish status every 5s
 if(now-lastStatus>5000)
 {
  lastStatus=now;

  publishStatus();
 }
}
```

```
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS D2

const char* ssid = "IOT11";
const char* password = "iotempire";
const char* mqtt_server = "192.168.1.1";

WiFiClient espClient;
PubSubClient client(espClient);

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

unsigned long lastMsg=0;

void setup_wifi()
{
  WiFi.begin(ssid,password);

  while(WiFi.status()!=WL_CONNECTED)
  {
    delay(500);
  }
}

void reconnect()
{
  while(!client.connected())
  {
    client.connect("tempNode");
    delay(500);
  }
}

void setup()
{
  Serial.begin(115200);

  sensors.begin();
  Serial.print("Devices found: ");
  Serial.println(sensors.getDeviceCount());

  setup_wifi();

  client.setServer(mqtt_server,1883);
}

void loop()
{
  if(!client.connected())
  {
    reconnect();
  }

  client.loop();

  unsigned long now=millis();

  if(now-lastMsg>3000)
  {
    lastMsg=now;

    sensors.requestTemperatures();

    float temp=sensors.getTempCByIndex(0);

    char msg[10];

    dtostrf(temp,1,2,msg);

    client.publish("hvac/room1/temperature",msg);

    Serial.println(msg);
  }
}
```

Then I went into node red and created all the required debuggers, listeners, and UI switches. Created a nice dashboard as well. All of the pictures are also available.

I also built the simulators in node red. It was pretty simple. I made it very basic and used code like this:

```
var t=context.get("t")||20;
var d=context.get("d")||1;

t+=d*0.5;

if(t>30)d=-1;
if(t<18)d=1;

context.set("t",t);
context.set("d",d);

msg.payload=t;

return msg;
```

```
if(msg.payload=="ON")
{
 msg.color="red";
 msg.payload="AC ON";
}
else
{
 msg.color="blue";
 msg.payload="AC OFF";
}

return msg;
```

I used MQTT elements, function elements and UI elements. Forgot to take a picture :(

Overall, I had some problems but I figured them out with the help of other students.

## Reflection 6
[Reflection 6](/Reflections/ref06.md)