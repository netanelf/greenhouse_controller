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
