#!/usr/bin/python
import os
import sys
import time
import sqlite3 as lite
from time import localtime, strftime
import os.path
import argparse


con = None
debug = None

def sendReading(id,weight):
	## connect to the database
	con = lite.connect('/usr/local/CoffeeScale/c16')
	cur=con.cursor()

	#time of insert:
	rightnow=str(strftime('%Y-%m-%d %H:%M:%S', localtime()))
	if debug: print "rightnow: " + rightnow 

	sql = "insert into readings(reading_time,reading_value,reading_units,scale_id) values ('%s', '%s', '%s', '%s')"%(rightnow,weight,"g",id)
	cur.execute (sql)
	con.commit()
	if debug: print "insert into readings(reading_time,reading_value,reading_units,scale_id) values ('%s', '%s', '%s', '%s')"%(rightnow,weight,"g",id)


