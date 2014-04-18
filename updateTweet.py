#!/usr/bin/python

import sqlite3 as lite
import os
import sys
import subprocess
import time as t
from datetime import datetime
from dateutil import parser
import genSent


debug=1
if datetime.today().weekday() >4:
	if debug: print "it's the weekend"
	sys.exit(0)
if 6 > datetime.now().hour > 18:
	if debug: print "it's not time"
	sys.exit(0)


## should probably get these from the database..
full = float(5680)
empty = float(2240) # AKA "tare" - between 2244 and 2250 seems to be the tare for the air pots

con = None
sn=[]
sid=[]
sname=[]

contents = "coffee"

con = lite.connect('/usr/local/CoffeeScale/c16')
con.text_factory = str
con.row_factory = lite.Row
cur=con.cursor()
#for each scale, get its info (id, serial number, name)
cur.execute("select id,serialno,scale_name from scales")
scalerows = cur.fetchall()
rows=len(scalerows)
if debug: print str(rows)+" scales"
for scale in scalerows:
	sn.append(str(scale["serialno"]))
	sid.append(str(scale["id"]))
	sname.append(str(scale["scale_name"]))

## for each scale tweet the weight
for i in (0,rows-1):	
	## get a sentence to tweet
	msg = str(genSent.main())
	while len(msg) > 110:
		msg = str(genSent.main())
	
	now = datetime.now()

	serialno=sn[i]
	scale_id=sid[i]
	scale_name=sname[i]
	if debug: print "\n"+scale_name +" "+ str(now)
	cur.execute("select * from readings where reading_time = (select MAX(reading_time) from readings where scale_id = ?)",scale_id)
	row=cur.fetchone()
	weight=row["reading_value"]
	# don't tweet that there is more than possible
	if weight<full+(full*.02):	
		oz = round(((weight-empty)*.035274),1)
		if oz>0:
			msg += "\n"+str(oz)+"oz-" +scale_name+"\nupdateTweet"
			if debug: print "------tweeting:\n"+msg+"\n-------"
			subprocess.call(["/usr/local/CoffeeScale/tweet.py",msg])
		
	smsmsg=str(oz)+" ounces remain in "+scale_name
#subprocess.call(["/usr/local/CoffeeScale/sendsms.py",smsmsg])

cur.execute("INSERT INTO tweets (tweet_time,scale_id,message) VALUES (?,?,?)",(str(now),str(scale_id),msg))
con.commit()
	
	