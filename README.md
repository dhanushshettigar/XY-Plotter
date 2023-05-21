# X-Y Plotter

This project is about a mechanical prototype of an X-Y axis plotter using the GRBL library. Text-to-speech is converted using an Android application, and the text is sent using Bluetooth, which is received by a Raspberry Pi. With the help of the HF2GCODE library, we generate G-code for the received text.

## TEXT TO GCODE

Use HF2GCODE library to convert text to cnc code(g-code).Clone my repo for required files.

```bash
unzip hf.zip
cd hf2gcode-master/src
make # COMPILE THE C SOURCE CODE
mv hf2gcode-master h2g # RENAME FOLDER
```
Test the HF2GCODE library

```bash
cd h2g/src
./hf2gcode -font "rowmans" -y 0 -x 0 -o text.gcd --min-gcode "Hello There!"
```

Source code : https://github.com/Andy1978/hf2gcode
    
## G Codes Explained

https://www.linuxcnc.org/docs/html/gcode/g-code.html#gcode

## Arduino GRBL Firmware Installation

1.Download grbl-corexy-servo.zip from my repo

2.Open Arduino IDE > Sketch > Include Library > Add .ZIP Library > grbl-corexy-servo.zip

3.Open Documents > Arduino > libraries > grbl-corexy-servo > examples > grblUpload > grblUpload.ino

4.Compile and Upload Grbl Code to your Arduino

## Mechanical Setup

[DIY](https://arnabkumardas.com/cnc.html)

[3D Printed Parts](https://www.3dindia.in/product-page/plastic-axidraw-clone-body-3d-parts-only-drawing-robots-with-arduino-casing)

[Assembly](https://www.youtube.com/watch?v=u26Wt8eY5zc)