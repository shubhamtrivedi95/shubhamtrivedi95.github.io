---
{
  "title": "UltraDistSensor: an Arduino ultrasonic sensor library",
  "summary": "A reusable HC-SR04 interface with public source, examples, and an Arduino library directory listing.",
  "category": "project",
  "status": "Published library",
  "featured": true
}
---

## The problem

Ultrasonic ranging involves configuring pins, triggering a measurement, and handling the echo pulse. Repeating this setup in each Arduino sketch makes experimentation harder to maintain.

## My implementation

I created UltraDistSensor to package the HC-SR04 interface as an Arduino library. Its documented API includes sensor attachment, distance readings in centimeters and inches, and echo timeout configuration. The directory listing also describes use with ping sensors and multiple sensors.

## Inspect the implementation

- [Source repository and documented API](https://github.com/shubhamtrivedi95/UltraDistSensor)
- [Example sketches](https://github.com/shubhamtrivedi95/UltraDistSensor/tree/master/examples)
- [Arduino Libraries directory entry](https://www.arduinolibraries.info/libraries/ultra-dist-sensor)

The directory records version 1.1.0, released July 26, 2021. That listing is evidence of distribution, not a measure of adoption.

## Boundaries

Sensor accuracy depends on the hardware and operating conditions. Review the current source, examples, and license information before reuse.
