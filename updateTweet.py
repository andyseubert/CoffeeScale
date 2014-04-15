#!/usr/bin/python

import sqlite3 as lite
import os
import sys
import subprocess
import time as t
from datetime import datetime
from dateutil import parser
import genSent


debug=0 
if datetime.today().weekday() >4:
	if debug: print "it's the weekend"
	sys.exit(0)
if 6 > datetime.now().hour > 18:
	if debug: print "it's not time"
	sys.exit(0)

#needs an argument. Tell me which scale wants to be tweeted...
if len(sys.argv) == 1:
	print "Tell me which scale wants to be tweeted..."
	sys.exit(0)

## should probably get these from the database..
full = float(5680)
empty = float(2240) # AKA "tare" - between 2244 and 2250 seems to be the tare for the air pots

scale_id=sys.argv[1]
weight = float(sys.argv[2])
# don't tweet that there is more than possible
if weight>full:sys.exit(0)

con = None

msg = str(genSent.main())

now = datetime.now()

contents = "coffee"
cups="0"

con = lite.connect('/usr/local/CoffeeScale/c16')
con.text_factory = str
con.row_factory = lite.Row
cur=con.cursor()
# get scale name from the database

cur.execute("select id,serialno,scale_name from scales where id="+scale_id)
scalerow = cur.fetchone()
scale_name = (str(scalerow["scale_name"]))

oz = str(round(((weight-empty)*.035274),1))

msg += "\n"+scale_name+"\n"+oz+" oz" + "\nupdateTweet.py" 

subprocess.call(["/usr/local/CoffeeScale/tweet.py",msg])

smsmsg=oz+" ounces remain in "+scale_name
#subprocess.call(["/usr/local/CoffeeScale/sendsms.py",smsmsg])

cur.execute("INSERT INTO tweets (tweet_time,scale_id,message) VALUES ('"+str(now)+"','"+str(scale_id)+"','"+msg+"')")
con.commit()
	
	