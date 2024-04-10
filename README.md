# Hello

This is the Git repository for my CNIT 361 final project, which is an analog gauge that displays a resource usage statistic of your computer. 

# Requirements

- Your computer, which has [HWiNFO](https://www.hwinfo.com/download/) installed
- Raspberry Pi (or equivalent Python & GPIO equipped device)
- 3 or 5 volt gauge
- LED lights (heavily emphsized)
- [MCP4725 DAC](https://www.adafruit.com/product/935)
- [USB-TTY Serial Cable]([url](https://www.adafruit.com/product/954)), and its [drivers]([url](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers?tab=downloads))

# Setup

## Wiring

1. Soldier the DAC to its pins and wire it accordingly.
2. Wire the gauge to the output of your DAC.
3. Wire up the LEDs to GPIO pins, and take note of their numbers.
4. Wire the TTY cable to your Pi, and insert the USB side into your computer. 

## Computers

### Your Computer

1. Enter the Sensors panel of HWiNFO, enter its settings, click the HWiNFO Gadget tab, then select the values you want to show on the gauge. (Recommended: Physical Memory Load, Core Usage, GPU Core Load, Current DL Rate, Current UP Rate)
2. Clone this repo to your desktop computer, and unzip it. The host file is what is relevant to you on this computer.
3. Edit the main.py file in the Host folder. Make necessary adjustments to serial_name, tracked_statistics, and any other values as you see fit.
4. Run the batch file.

### Raspberry Pi

1. Activate the serial, SCL, and SDA GPIO pins. Ensure serial does not use login. 
2. Edit the main.py file in the PiClient folder. Edit available_lights to include the GPIO pins you wired your LEDs into. Order sensitive.
3. Execute the start.sh file. 
