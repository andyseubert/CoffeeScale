#!/usr/bin/python
import usb.core
import usb.util
import os
import sys
import sqlite3 as lite
from time import localtime, strftime

VENDOR_ID = 0x0922 # dymo vendor
PRODUCT_ID = 0x8004 # 25lb scale -- other dymo scales have different product_ids
DATA_MODE_GRAMS = 2
DATA_MODE_OUNCES = 11

# connect to database
con = None
debug = 1
con = lite.connect('/usr/local/CoffeeScale/c16')
cur=con.cursor()

# find the USB Dymo scale devices
#device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
devices = usb.core.find(find_all=True, idVendor=VENDOR_ID)

sys.stdout.write('There are ' + str(len(devices)) + ' scales connected!\n')
scales=[]
i=1
for device in devices:
	scalename="ChangeMyName "+str(i)
	print "scale #" + str(i)
	devbus = str(device.bus)
	devaddr = str(device.address)
	productid=str(device.idProduct)
# help found here http://stackoverflow.com/questions/5943847/get-string-descriptor-using-pyusb-usb-util-get-string
	serialno = str(usb.util.get_string(device,256,3))
	manufacturer = str(usb.util.get_string(device,256,1))
	description = str(usb.util.get_string(device,256,2))
	if debug:
		print serialno
		print manufacturer
		print description
# look for serialnumber already existing
	cur.execute("select count(*) from scales where serialno='"+serialno+"'")	 
# this should produce ONE row but in case it does not I'll refer to the rows by their numeric index
	row = cur.fetchone()[0] # fetchall so we can refer to the columns by name
	if row >=1 :
		print "row:" + str(row)
		print "serial "+serialno+" already exists in database"
	else:
		sql = "insert into scales(scale_name,vendor_id,product_id,data_mode_grams,data_mode_ounces,serialno) values ('%s', '%s', '%s', '%s', '%s', '%s')"%(scalename,str(VENDOR_ID),productid,str(DATA_MODE_GRAMS),str(DATA_MODE_OUNCES),serialno)
		if debug:print sql
		cur.execute (sql)
		con.commit()
		if debug: print "inserted new scale with serial "+serialno+" in database"
	i+=1
cur.close()

for device in devices:	
	try:
		device.detach_kernel_driver(0)
	except Exception, e:
		pass
	
	
