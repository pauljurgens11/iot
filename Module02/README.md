# Module 2

We are going to show here notes for Task 1, 2, 3, 4, and 5 to prove

## General notes

- LED -> diode (anode + -> cathode -)
  - need a current limiting resistor to protect LED (so not too much power goes through it)

## Task 1 - Breadboards and Electronic Prototyping Intro

Electric Circuit

- Closed loop → current flows
- Components: power source, conductors, load, switch (optional)
- Basic properties: voltage (V), current (I), resistance (R)
- Ohm’s Law: V = I · R

Breadboard

- Solderless prototyping board
- Used to quickly test circuits
- Connected rows internally (horizontal strips in center)
- Power rails on sides (long vertical + / – lines)
- Reusable, no permanent soldering

Cable Color Conventions

- Red = VCC / +5V
- Black = GND
- (Often) Yellow/Green/Blue = signal

Wiring an LED to 5V

- 5V → resistor → LED anode (long leg)
- LED cathode (short leg, flat side) → GND
- Resistor required
- Prevents overcurrent

LED (Light Emitting Diode)

- Semiconductor device
- Emits light when forward biased
- Low power, long lifetime

What is special about diodes?

- Current flows only one direction
- Has forward voltage drop (~2V red, ~3V white/blue)
- Polarity matters

Something very important

- Do not connect LED without resistor

## Task 2 - Collect Hardware

TODO: add pictures

Collected all the hardware:

One blue bag for keeping all your IoT parts (maybe several small plastic bags for keeping smaller parts like resistors and diode)
One big, one medium size breadboard
Dupont cables - about 20 of each type (there are three types - which and why?), varying colors
2-5 Leds/Unicolor (2 pins)
2-5 resistors >150 Ohm (<1kOhm)
3 buttons
2 Wemos D1 Mini + 2 USB cables
USB Charger (MH-KC24-4) + 12V Power-Supply + Y-cable
If enough present also one multimeter

## Task 3 -  “Hello World” Electronic Prototyping

- hello world of electronics -> turn on a LED
- got it working quite easily
  - it was a bit confusing at first but once i watched the video, it became clearer
- pictures show my work

## Task 4 - Fritizing, SimulIDE, or Cirkit Designer

- got it working in Cirkit quite easily
- image in pictures

## Task 5 - Blink on the Wemos D1 Mini

- got it working (on board LED, D6 and D4).
- image in pictures

## Task 6 - Toggle LED with Button

pull up resistor
- Prevents floating input
- Stabilizes digital inputs

- Wemos D1 Mini is 3.3V

- got it working
- used INPUT_PULLUP
- serial output changes between 0 and 1

## Task 7 - Relay-Lock Button

Got the solenoid working well using the relay. It clicked on button press. Had some help from TA.

Relay
- Electrically controlled switch
- Uses a coil (electromagnet) to move mechanical contacts
- Provides electrical isolation between control and load

Solenoid
- Electromagnetic locking mechanism
- Coil
- Movable pin

Also completed the last bullet point. All worked (clicking in a loop, serial input usage, separate Wemos pin connection with button).

At first we misunderstood that we needed to connect 2 separate Wemos.

## Task 8 - LED Fade (optional task for advanced students)

Didn't get it fully working but almost... Moved on to another task

PWM
- Digital signal switching between 0V and 3.3V
- Rapid on/off switching at fixed frequency
- Duty cycle (%) controls average voltage

## Reflection 2
[Reflection 2](/Reflections/ref02.md)

## Task 9

We learned about the different buses and experimented with them. Overall was successful. I have attached some images here and some images are in my partner's repository:

https://github.com/NickPoint/IoT/tree/main/Module02

Initially we had some trouble with the temperature sensor and touch sensor but after experimenting and googling, we got it working.

RGB LED code we used is here (generated partly by ChatGPT model 5 with some changes added by ourselves):

```
#define RED D5
#define GREEN D6
#define BLUE D7

void setColor(int r, int g, int b) {
  analogWrite(RED, r);
  analogWrite(GREEN, g);
  analogWrite(BLUE, b);
}

void setup() {
  Serial.begin(115200);

  pinMode(RED, OUTPUT);
  pinMode(GREEN, OUTPUT);
  pinMode(BLUE, OUTPUT);
}

void loop() {

  Serial.println("Red");
  setColor(1023,0,0);
  delay(1500);

  Serial.println("Green");
  setColor(0,1023,0);
  delay(1500);

  Serial.println("Blue");
  setColor(0,0,1023);
  delay(1500);

  Serial.println("Yellow");
  setColor(1023,1023,0);
  delay(1500);

  Serial.println("Purple");
  setColor(1023,0,1023);
  delay(1500);

  Serial.println("Cyan");
  setColor(0,1023,1023);
  delay(1500);
}
```

## Reflection 3
[Reflection 3](/Reflections/ref03.md)
