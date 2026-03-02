# greenhouse_controller
## Introduction
Greenhouse Controller is a self-contained monitoring and irrigation control system for long-term autonomous operation in a home environment.
It includes a web interface for viewing state and setting up the system

## Overview
The project includes interfacing with temperature, homidity and light sensors.
Controlling relays that can controll water flow or other outputs.
Interfacing with a camera to save ongoing still images.

The architecture was designed for running on a raspberry pi, using its IOs through a dedicated hat board that interfaces directrly with sensors and relays.
key points:
1. to expand the output amount of the digital IOs a 74HC595A shift register was used.
3. the board includes:
   1. connector for external 5V power that can run the board and/or the hat (controlled with a soldered jumper)
   2. 4 outputs that can controll a SSR/ Relay with connectors for an indicater LED (board includes a current limiting resistor)
   3. 4 outputs of raw digital pins from the shift register (no LED/ Driver/ protection)
   4. 4 connectors for an I2C sensors, conenctors include the communication pins (sca,sda) and a 3.3/4V supply selected with a soldered jumper
   5. 3 dedicated connectors for a "Maxim Integrated DS18B20" 1-wire thermometer
   6. 3 dedicated connectors for a "AM2302/DHT22" digital temperature and humidity sensor
   7. pins for interfacing with all the Rpi GPIOs (40p connector)
   8. pads for the shift register, driving transistors, and passive components

The project was built usind the Dgango python library that implements the backend and frontend.
Drivers for interacting with some sensors were implemented or if were already implemented, open source implementations were used.
for example:
1. Maxim Integrated DS18B20 thermometer
2. AM2302/DHT22 tmperature and humidity sensor
3. generic water flow sensor (pulse per known amount of flow)
4. TSL2561 Lux sensor
5. generic digital Input/ Output lines (can be used for level sensors etc.)
6. a camera driver (uses the Rpi camera interface)
   
## hat board schematic and layout

![image of the board schematics file](greenhouse_controller_expansion_board/output/greenhouse_controller_schematic.png)

![image of the board layout file](greenhouse_controller_expansion_board/output/greenhouse_controller_layout.png)

## Controll options
The project implements an "Event -> Condition -> Action" Flow. 
Events can be configured (for example and event when a certain time elapses), 
conditions can be configures (only do X if ...) and actions can be configured (for example, change state of relay "Y").

an example watering flow can be:
- at 8:00 of days 1,3,5:
	- turn ON relay A
	- wait 10 minutes
	- turn OFF relay A

another flow can be to save sensor images to a DB:
- avery 5 minutes:
  - read sensor A, save value to DB
  - read sensor B, save value to DB
  - ...
 
## web UI

The django admin interface can be used to create new flows (events, actions and conditions) (or this can be done via a python script upon deploying
The web interface includes views of current sensors values current relays states, last image from the camera and more.
There also a manual operation page for manually controlling things (without using flows)

## deployment
1. clone https://github.com/netanelf/greenhouse_controller.git
2. clone https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code.git
3. install: 
	python-django python-smbus i2c-tools build-essential python-dev python-openssl
4. git clone https://github.com/adafruit/Adafruit_Python_DHT.git, 
	cd Adafruit_Python_DHT
	sudo python setup.py install
5. if you want controller automatic startup - add ```@lxterminal -e '/home/pi/workspace/greenhouse_controller/run_full_linux.sh'``` to /etc/xdg/lxsession/LXDE-pi/autostart

web (new):
1. delete db.sqlite3 (if exists)
2. delete all migrations
3. manage.py makemigrations greenhouse_app
4. manage.py migrate --database='backup'
5. manage.py migrate --database='default'
6. python populate_greenhouse_app_rpi.py

web (save db):
1. manage.py makemigrations
2. manage.py migrate --database='backup'
3. manage.py migrate --database='default'

## Lessons Learned
### Database on a Raspberri Pi
1. Because Rpi is slow (especially the flash memory) we keep db.sqlite3 small as possible
2. All measurements from db.sqlite above some number (64K?) are moved to another db backup.sqlite3
3. backup.sqlite3 can be copied regularly to a strong computer

