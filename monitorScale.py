#!/usr/bin/python
import os
import sys
import time
from sendReading import *
import sqlite3 as lite
from time import localtime, strftime
import os.path
import usb.core
import subprocess
########### 4 scoops == 226 grams
con = None
debug = 0
interface = 0
pushing = None
firstrun=1
readmillis = 0
# twitter note
# andy@collegenet.com
# CNtwitterCoffee16
# @cnCoffeePoton16
## connect to the database
con = lite.connect('/usr/local/CoffeeScale/c16')
con.text_factory = str
cur=con.cursor()

#get the scale serial numbers and ids from the database
cur.execute("select id, serialno from scales")
scalerows = cur.fetchall()
serialnos={}
lastreading={}

for scale in scalerows:
	serialnos[scale[0]]=scale[1] 
	lastreading[int(scale[0])] = 0

con.close()

VENDOR_ID = 0x0922
PRODUCT_ID = 0x8004
DATA_MODE_GRAMS = 2
DATA_MODE_OUNCES = 11
	
# find the USB Dymo scale devices
devices = usb.core.find(find_all=True, idVendor=VENDOR_ID)
		
while 1:
	for i, s in serialnos.items():		
		serialno=str(s)
		id=str(i)
		if debug: 
			print "\nscale serial:"+serialno+" is id "+id
			print "last reading: "+str(lastreading[i])
		time.sleep(.5) # please only one reading per second 
		subprocess.call(["/usr/local/CoffeeScale/events.py"])
		## read the live scale value
## read loop
		for device in devices:	
			if device.is_kernel_driver_active(0) is True:
				device.detach_kernel_driver(0)
			devbus = str(device.bus)
			devaddr = str(device.address)
			productid=str(device.idProduct)
			try:
				if str(usb.util.get_string(device,256,3)) == serialno:
					if debug: print "scale id:" + id + " serial: "+ serialno
					if debug: print ("device serial:    <" + str(usb.util.get_string(device,256,3))) + ">"
					## set USB device endpoint here
					endpoint = device[0][(0,0)][0]
					# read a data packet
					attempts = 10
					data = None						
					while data is None:# and attempts > 0:
						try:
							data = device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
							if debug: print "data: "+str(data)
						except usb.core.USBError as e:
							data = None
							if e.args == ('Operation timed out',):
								attempts -= 1
								print e
								continue
					
					# The raw scale array data
					#print data
					raw_weight = data[4] + (256 * data[5])

					if data[2] == DATA_MODE_OUNCES:
						ounces = raw_weight * 0.1
						weight = "%s oz" % ounces
					elif data[2] == DATA_MODE_GRAMS:
						grams = raw_weight
						weight = "%s g" % grams
						
					reading = weight
					if debug: print "raw reading '" + reading +"'"
					readval = float(reading.split(" ")[0])
					readunit = reading.split(" ")[1]
					## if the units are ounces ("oz") then convert to "g"
					if readunit == "oz" and readval !=0:
						readval = readval*28.3495
						readunit="g"
						if debug: print "converted oz to g"
					if debug: print "current weight : '" + str(readval) +"' "+readunit
					if debug: print "current time   : "+strftime("%Y-%m-%d %H:%M:%S", localtime())
					readval = round(readval)
					if debug: print "rounded read value is: " +str(readval)
					## compare the cached value with the current value
					if (readval != float(lastreading[i])) or (int(round(time.time() * 1000)) - readmillis) > 5:
						## if different then update the database and update the cache
						
						# determine the magnitude of the change here
						delta = abs(readval - float(lastreading[i]))
						# a small change of a few grams should not be noted
						if 10 < int(delta) < 6000 : #or (int(round(time.time() * 1000)) - readmillis) > 5: 
							if (readval != float(lastreading[i])):
								if debug:
									print "delta: " + str(delta) + " not ignoring"
									print "scale "+id+" reading changed from "+str(lastreading[i])+" to "+str(readval)
								sendReading(id,readval)	
								#subprocess.call(["/usr/local/CoffeeScale/updateTweet.py",id,str(readval)])
							readmillis = int(round(time.time() * 1000))
					else:
						if debug: print "reading unchanged"
					## set the last read value to the current read value 
					lastreading[i] = readval
			except usb.core.USBError as e:
				print "usb core error:"
				print e
#			if debug: print "release claimed interface"
#			usb.util.release_interface(device, interface)
	if debug: print ""
			
			
			
