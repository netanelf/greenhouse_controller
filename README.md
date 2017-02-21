# greenhouse_controller

1. clone https://github.com/netanelf/greenhouse_controller.git
2. clone https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code.git
3. install: 
	python-django python-smbus i2c-tools build-essential python-dev python-openssl
4. git clone https://github.com/adafruit/Adafruit_Python_DHT.git, 
	cd Adafruit_Python_DHT
	sudo python setup.py install
5. autostartup by adding "@lxterminal -e '/home/pi/workspace/greenhouse_controller/run_full_linux.sh'" into ~/.config/lxsession/LXDE-pi
6. tightvnc apparently opens another session therefore when it starts - the script is ran again, do not use (X11vnc on session 0 should work)


web:
1. delete db.sqlite3 (if exists)
2. delete all migrations
3. manage.py makemigrations greenhouse_app
4. manage.py migrate --database='backup'
5. manage.py migrate --database='default'
6. python populate_greenhouse_app_rpi.py


comments:
1. Because Rpi is slow (especially the flash memory) we keep db.sqlite3 small as possible
2. All measurements from db.sqlite above some number (64K?) are moved to another db backup.sqlite3
3. backup.sqlite3 can be copied regularly to a strong computer

