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

## Reflection 6
[Reflection 6](/Reflections/ref06.md)