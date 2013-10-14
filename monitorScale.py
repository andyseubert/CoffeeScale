#!/usr/bin/python
import os
import sys
import time
from sendReading import *
import MySQLdb as mdb
from time import localtime, strftime
import os.path
import usb.core

con = None
debug = 0
interface = 0
pushing = None
firstrun=1
# twitter note
# andy@collegenet.com
# CNtwitterCoffee16
# @cnCoffeePoton16
## connect to the database
con = mdb.connect('localhost', 'coffeeuser', 'coffee16', 'coffeedb');
cur = con.cursor(mdb.cursors.DictCursor)
#get the scale serial numbers and ids from the database
cur.execute("select id,serialno from scales")
scalerows = cur.fetchall()
serialnos={}
lastreading={}
for scale in scalerows:
	serialnos[scale["serialno"]]=scale["id"] 
	lastreading[str(scale["id"])] = 0

cur.close()

VENDOR_ID = 0x0922
PRODUCT_ID = 0x8004
DATA_MODE_GRAMS = 2
DATA_MODE_OUNCES = 11

# find the USB Dymo scale devices
devices = usb.core.find(find_all=True, idVendor=VENDOR_ID)
		
while 1:
	for s, i in serialnos.items():		
		serialno=str(s)
		id=str(i)
		if debug: print
		time.sleep(.5) # please only one reading per second
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
						if debug: print "converted oz to g"
					if debug: print "current weight : '" + str(readval) +"' "+readunit
					if debug: print "current time   : "+strftime("%Y-%m-%d %H:%M:%S", localtime())
					
					## compare the cached value with the current value
					if (readval != float(lastreading[id])) or (int(round(time.time() * 1000)) - readmillis) > 5:
						## if different then update the database and update the cache
						
						# determine the magnitude of the change here
						delta = abs(readval - float(lastreading[id]))
						# a small change of a few grams should not be noted
						if delta > 5 or (int(round(time.time() * 1000)) - readmillis) > 5: 
							# update it by sending the serial and weight to another program and not waiting for it to return..
							if (readval != float(lastreading[id])):
								print serialno+" reading changed from "+str(lastreading[id])+" to "+str(readval)
								sendReading(id,readval)							
							readmillis = int(round(time.time() * 1000))
						## if its a huge change, someone has pressed the handle - except when they are returning the pot... or this is the first reading
						if delta > 800 :
							# see if it's a positive or negative change
							if ( readval > lastreading[id]):
								# push started
								print "push start"
								prepush=lastreading[id]
							else:
								#push ended
								print "push end"
								## here you might calculate the amount removed by the push if you knew the reading before the push started...
								print "removed "+str(readval-prepush)+" g"
														
					else:
						if debug: print "reading unchanged"
					## set the last read value to the current read value 
					lastreading[id] = readval
			except usb.core.USBError as e:
				print "usb core error:"
				print e
#			if debug: print "release claimed interface"
#			usb.util.release_interface(device, interface)
	if debug: print ""
			
			
			