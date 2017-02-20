# greenhouse_controller

1. clone https://github.com/netanelf/greenhouse_controller.git
2. clone https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code.git
3. install: 
	python-django python-smbus i2c-tools build-essential python-dev python-openssl
4. git clone https://github.com/adafruit/Adafruit_Python_DHT.git, 
	cd Adafruit_Python_DHT
	sudo python setup.py install


web:
1. delete db.sqlite3 (if exists)
2. delete all migrations
3. manage.py makemigrations greenhouse_app
4. manage.py migrate --database='backup'
5. manage.py migrate --database='default'
6. python populate_greenhouse_app_rpi.py

