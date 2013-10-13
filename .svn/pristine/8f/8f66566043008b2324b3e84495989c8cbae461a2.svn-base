#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys
from readscale import *
from time import localtime, strftime
#from warnings import filterwarnings
print "Content-type: text/html\n\n"

con = None
debug = None 
reading = readScale(1,8)
readval = reading.split(" ")[0]
readunit = reading.split(" ")[1]
print "current weight : " +str(readval)+" "+readunit+"<br />\n"
print "current time   : "+strftime("%Y-%m-%d %H:%M:%S", localtime())+"<br />\n"

try:
	con = mdb.connect('localhost', 'coffeeuser', 'coffee16', 'coffeedb');
	cur = con.cursor(mdb.cursors.DictCursor)
	# get most recently added reading
	cur.execute("select * from readings where reading_time = (select MAX(reading_time) from readings)")	 
# this should produce ONE row but in case it does not I'll refer to the rows by their numeric index
	rows = cur.fetchall() # fetchall so we can refer to the columns by name
	if debug: print "most recent reading time: " + str(rows[0]["reading_time"])
	if debug: print "most recent value : " + str(rows[0]["reading_value"])
	lastreading = rows[0]["reading_value"]
	lastreadtime = rows[0]["reading_time"]
# NEW SCALE VALUE?
	if float(lastreading) != float(readval):
		cur.close()
		cur = con.cursor()
		rightnow=str(strftime('%Y-%m-%d %H:%M:%S', localtime()))
		#print "rightnow: " + rightnow + "<br />\n"
		sql = "insert into readings(reading_time,reading_value,reading_units) values ('%s', '%s', '%s')"%(rightnow,readval,readunit)
		#print sql
		cur.execute (sql)
		con.commit()
		#print "insert into readings(reading_value, reading_time, reading_units) values ('"+ readval +"','"+ rightnow +"','g')"
		print "inserted new reading in database"
	else:
		print "reading unchanged"
# LONG TIME SINCE LAST READING?

except mdb.Error, e:
  
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)
    
finally:    
        
    if con:    
        con.close()
