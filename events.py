#!/usr/bin/python

# these are my notes to-do not what currently exists...
#events
#- full [ reading within a few ounces of full value ]
#- just filled [ one large value preceded by zero ]
#- some was just removed [ most recent reading less than the reading just before that ]
#- almost empty [ reading < 12 ounces more than empty value ]
#- empty [ reading < 4 ounces more than empty value ]
#- being filled [ zero reading ]
#- missing for more than twice the time it takes to fill it up [ last reading was more than 12 minutes ago and still 0]
#
#
#what time is it now?
#
#get the last recorded reading
#    what time was the last recorded reading submitted?
#        was it less than one minute ago?
#            yes --
#            no --- 
#        was it more than 30 minutes ago?
#            yes --
#            no --- 
#        
import sqlite3 as lite
import os
import sys
import subprocess
import time as t
from datetime import datetime
from dateutil import parser
import canisms
from canisms import main

debug = 1
recipient="5035228381@vtext.com"


if debug: print "This is hour "+str(datetime.now().hour)

if datetime.today().weekday() >4:
	if debug: print "it's the weekend"
	sys.exit(0)
if 6 > datetime.now().hour > 18:
	if debug: print "it's not time"
	sys.exit(0)

con = None
sn=[]
sid=[]
sname=[]
i=0
msg=""

## should probably get these from the database..
full = float(5622)
empty = float(2240) # AKA "tare" - between 2244 and 2250 seems to be the tare for the air pots
contents = "coffee"

con = lite.connect('/usr/local/CoffeeScale/c16')
con.text_factory = str
con.row_factory = lite.Row
cur=con.cursor()
# get scale info from the database
# how many scales are there? 

#for each scale, get its info (id, serial number, name)
cur.execute("select id,serialno,scale_name from scales")
scalerows = cur.fetchall()
rows=len(scalerows)
if debug: print str(rows)+" scales"
for scale in scalerows:
	sn.append(str(scale["serialno"]))
	sid.append(str(scale["id"]))
	sname.append(str(scale["scale_name"]))
	i+=1

## for each scale check for events..
for i in (0,rows-1):		
	now = datetime.now()
	serialno=sn[i]
	scale_id=sid[i]
	scale_name=sname[i]
	if debug: print "\n"+scale_name +" "+ str(now)
	# get the last 2 readings
	cur.execute("SELECT reading_value,reading_units,scale_id,reading_time FROM readings where scale_id="+scale_id+" ORDER BY reading_time DESC LIMIT 2")
	while True:
	## first row is the NEWER of the two readings
		reading=cur.fetchone()
		if reading==None:
			break
		newest_value = reading["reading_value"]
		newest_units = reading["reading_units"]
		newest_time  = reading["reading_time"]
		if debug : print "newest row for scale #"+str(scale_id)+" value "+str(newest_value)+newest_units+" at "+str(newest_time)
	## second row is THE OLDER reading
		reading=cur.fetchone()
		if reading==None:
			break
		second_value = reading["reading_value"]
		second_units = reading["reading_units"]
		second_time  = reading["reading_time"]
		if debug : print "second row for scale #"+str(scale_id)+" value "+str(second_value)+second_units+" at "+str(second_time)
		
	## now we have the last 2 readings.
## How many ounces are left?
	if newest_value > 0:
		remainingoz = round(((newest_value-empty)*.035274),1)
	else:
		remainingoz = 0
	if debug: print str(remainingoz) +" ounces remain of "+ scale_name
	
## NEARLY EMPTY HERE	only care if the newest_time is less than one minute ago
	then = parser.parse(newest_time)
	timediff=round( (now - then ).total_seconds() / 60)
	if debug: print "timediff is "+str(timediff)
	if remainingoz < 24:
		if timediff <2:
			msg=scale_name+" just became almost empty. "+str(remainingoz)+" ounces remain"
		if timediff >2:
			msg=scale_name+" is almost empty. "+str(remainingoz)+" ounces remain and has been for "+str(timediff)+" minutes"
		## check to see if it's cool to sms
		if (canisms.main(scale_id,"almostempty",recipient)):
#               ## put a new row in the database indicating a new sms was sent
			cur.execute("INSERT INTO texts (sms_time,scale_id,msg,type,recipient) VALUES (?,?,?,?,?)",(str(now),str(scale_id),msg,"almostempty",recipient))
			con.commit()		
			if debug: print msg
			subprocess.call(["/usr/local/CoffeeScale/sendsms.py",msg])
## Missing from scale for longer than it takes to refill
	if remainingoz == 0 and timediff > 10:
		msg=scale_name+" is done brewing"
		## check to see if it's cool to sms
		if (canisms.main(scale_id,"donebrewing",recipient)):
#               ## put a new row in the database indicating a new sms was sent
			cur.execute("INSERT INTO texts (sms_time,scale_id,msg,recipient) VALUES ('"+str(now)+"','"+str(scale_id)+"','"+msg+"')")
			con.commit()		
			if debug: print msg
			subprocess.call(["/usr/local/CoffeeScale/sendsms.py",msg])
### freshly filled
	if remainingoz >= full and timediff <= 2:
		msg=scale_name+" has fresh coffee"
		## check to see if it's cool to sms
		if (canisms.main(scale_id,"freshcoffee",recipient)):
#               ## put a new row in the database indicating a new sms was sent
			cur.execute("INSERT INTO texts (sms_time,scale_id,msg,recipient) VALUES ('"+str(now)+"','"+str(scale_id)+"','"+msg+"')")
			con.commit()		
			if debug: print msg
			subprocess.call(["/usr/local/CoffeeScale/sendsms.py",msg])
			
		
		

		
#### SQL SNIPS
## get scale details	
# select id,serialno,scale_name from scales;
## get most recent readings
# select * from readings where reading_time = (select MAX(reading_time) from readings where scale_id = '2' );
# select * from readings where reading_time = (select MAX(reading_time) from readings where scale_id = '1' );
## get the last time the pot was filled
# select MAX(fulltime),reading_value FROM (select reading_time as fulltime,reading_value,scale_id from readings where reading_value >= 5622 AND reading_value <= 5900 AND scale_id = '2') xo
# select MAX(fulltime),reading_value FROM (select reading_time as fulltime,reading_value,scale_id from readings where reading_value >= 5000 AND reading_value <= 7000 AND scale_id = '1') xo
## various attempts which led me to realize 10lbs is insufficient..
# select MAX(reading_value) from readings WHERE scale_id=1
# select * from readings where scale_id=1 AND reading_value >= 4000 AND reading_value <= 6000
# select * from readings where scale_id=1 ORDER BY reading_value DESC
# select * from readings where scale_id=1 AND reading_value <= 6000 ORDER BY reading_value DESC


