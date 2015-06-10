CoffeeScale
===========

Read a USB scale with RaspBerryPi store the data in a database and display coffee status. 

Thanks to : http://steventsnyder.com/reading-a-dymo-usb-scale-using-python/
 for providing the starting point and the scale reading code
 
Requirements / Setup Commands
-----

 - packages
 
````bash
sudo apt-get update
sudo apt-get upgrade
apt-get -y remove festival apache2-mpm-prefork apache2-utils apache2.2-bin apache2.2-common libapache2-mod-php5
apt-get -y install mpg123  php5-sqlite man espeak sqlite3 subversion git openssh-server ntp lighttpd libusb-1.0 mysql-server python python-mysqldb php5 php5-mysql phpmyadmin python-setuptools python-pip python-dateutil ssmtp mailutils
pip install twython
pip install pyusb
 pip install shutil
````

 - PYUSB
 
https://github.com/walac/pyusb
````bash
wget https://github.com/walac/pyusb/archive/master.zip
unzip master.zip
 cd pyusb-master/
./setup.py install
````
sqlite setup
--
````bash
sqlite3 c16
````
CREATE TABLES 
--
````SQL
CREATE TABLE 'settings' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'setting_name' REAL NOT NULL, 'setting_value' REAL NOT NULL);
CREATE TABLE 'readings' (
  'reading_time' datetime NOT NULL,
  'reading_value' INTEGER NOT NULL,
  'scale_id' INTEGER NOT NULL,
  'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  'reading_units' varchar(10) NOT NULL);
CREATE TABLE 'scales' (
  'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'scale_name' TEXT NOT NULL,'vendor_id' TEXT NOT NULL,'product_id' TEXT NOT NULL,'serialno' TEXT NOT NULL,'data_mode_grams' INTEGER NOT NULL,'data_mode_ounces' INTEGER NOT NULL
  );
CREATE TABLE 'tweets' ('tweet_time' INTEGER NOT NULL, 'message' INTEGER NOT NULL, 'type' INTEGER NOT NULL default 'update', 'scale_id' INTEGER);
CREATE TABLE 'texts' (
  'sms_time' datetime NOT NULL,
  'msg' TEXT NOT NULL,
  'type' INTEGER NOT NULL,
  'scale_id' INTEGER NOT NULL,
  'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  'recipient' TEXT NOT NULL);

````

Connect the Scale
--

run dmesg to see if it is connected. the output should be almost exactly like this:
````bash
[61539.300131] usb 1-1.2.1.4: new full-speed USB device number 6 using dwc_otg
[61539.405516] usb 1-1.2.1.4: New USB device found, idVendor=0922, idProduct=8004
[61539.405548] usb 1-1.2.1.4: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[61539.405568] usb 1-1.2.1.4: Product: M25 25 lb Digital Postal Scale
[61539.405584] usb 1-1.2.1.4: Manufacturer: DYMO
[61539.405596] usb 1-1.2.1.4: SerialNumber: 0000000022159
[61539.437452] generic-usb 0003:0922:8004.0001: hiddev0: USB HID v1.01 Device [DYMO M25 25 lb Digital Postal Scale] on usb-bcm2708_usb-1.2.1.4/input0
````

bash script to extract the vendor id and product id (would be nice to use python to parse dmesg to grab the stuffs but that may not be feasible)
in fact this may not be necessary as the scale id's are always the same...

````bash
# this gets just the vendor id
dmesg | grep -B6 DYMO | grep idVendor | cut -d"=" -f2 | cut -d"," -f1
# this gets just the Product id
dmesg | grep -B6 DYMO | grep idProduct | cut -d"=" -f3
````

Run getscaleinfo.py
--
it should tell you how many scales are connected, and whether or not they exist in the database. If they don't exist, this will add them
````bash
root@c16:/usr/local/CoffeeScale# ./getscaleinfo.py
There are 2 scales connected!
scale #1
0000000022159
DYMO
M25 25 lb Digital Postal Scale
row:1
serial 0000000022159 already exists in database
scale #2
0000000038053
DYMO
M25 25 lb Digital Postal Scale
row:1
serial 0000000038053 already exists in database

````

Cron
--

add psmonitor.sh to the crontab - this will watch for the running monitorScale.py application and restart it if necessary.
````bash
* * * * * /usr/local/CoffeeScale/psmonitor.sh
````



Trouble
--
caused by udev permissions:
````sh
python /usr/local/CoffeeScale/readscale.py
usb.core.USBError: [Errno 13] Access denied (insufficient permissions)
````
 - the fix:
````bash
sudo vi /etc/udev/rules.d/98-dymo.rules
$ sudo cat /etc/udev/rules.d/98-dymo.rules
SUBSYSTEM=="usb", ATTR{idVendor}=="0922", ATTR{idProduct}=="8004", MODE="666"
````

Read the Scale
--
what if you have more than one scale?
according to pyusb documentation, usb devices sometimes have "bus" and "address" identifiers
````python
devices = usb.core.find(find_all=True, idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
sys.stdout.write('There are ' + str(len(devices)) + ' scales connected!\n')
if len(devices) > 1:
	print "more than one scale found"
else:
	print "devices bus: " + str(devices[0].bus)
	print "device address: " + str(devices[0].address)
````
they also show serial numbers and here is how to get them
````python
devices = usb.core.find(find_all=True, idVendor=VENDOR_ID)
sys.stdout.write('There are ' + str(len(devices)) + ' scales connected!\n')
scales=[]
i=1
for device in devices:
	scalename="scale "+str(i)
	print "scale #" + str(i)
	devbus = str(device.bus)
	devaddr = str(device.address)
	productid=str(device.idProduct)
# help found here http://stackoverflow.com/questions/5943847/get-string-descriptor-using-pyusb-usb-util-get-string
	serialno = str(usb.util.get_string(device,256,3))
	manufacturer = str(usb.util.get_string(device,256,1))
	description = str(usb.util.get_string(device,256,2))
````

read the scale should output just one number: the weight in grams
 
monitorScale.py
--

 - core of the system - runs constantly to read the scale(s) and determine if the reading changed
 - if the reading changes, send the new reading (time stamped) to the database via the script ````sendReading.py````
 
sendReading.py
--

 - imported into ````monitorScale.py```` via an include
 - sole purpose is to send a reading into the database and timestamp it. ````monitorScale.py```` sends the scale id and the weight values to this script for saving.
 
getscaleinfo.py
-- 

 - this script's sole purpose is to get the serial number and metadata from the scales and insert it into the database. 
 - it is the initial framework for part of the admin system
 
index.php
--

 - this is the initial web display. Currently uses javascript to query the script 'scaleReport.py'
````javascript
function getStatus() { 
    $('div#status').load('/cgi-bin/scaleReport.py');
    setTimeout("getStatus()",500); 
}
````
scaleReport.py
--

 - this scripts only job is to report the latest scale reading so the web page can grab it 
 - queries the database to determine how many scales exist in the database and creates ````<div> ```` sections for each one

 
 Running / Using
 -----
 
 - do the setup steps above (probably have to make the scripts executable)
 - put index.php in your web server document root
 - put sendReading in the web server's cgi-bin folder (or change the code in index.php to point to the correct place)
 - run getscaleinfo.py which will populate the scales table 
 - run monitorScale.py which will send readings into the readings table
 - load index.php in a web browser

 
TODO
--
 - not run as root!
 - triggered events
  - watch for and react to events such as
   - newly filled coffee pot
   - empty pot
   - draw from pumper
 - interact with web services
  - twitter
  - facebook
  - email
  - sms  
 - admin backend
  - ability to add and remove scales interactively
  - monitor alerts
  - reports on coffee consumption/activity
  - administer users
  - 
 - users
  - add user interface where users can sign up to receive alerts.
 - web display
  - more interactivity

update
02/8/2013
the SD card died so I have a new SD card and am glad I checked the code in
I am trying "mobiuslinux" for the distro this time:
http://moebiuslinux.sourceforge.net/ it is smaller and has no graphical stuff. I may come to need graphical stuff but for now just the basics will hopefully make a faster updating thinger

 

 

 

 

 

 

 

 
