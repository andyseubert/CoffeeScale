#!/usr/bin/python

# this reports the latest scale reading so the web page can grab it

import MySQLdb as mdb
import os
import sys
print "Content-type: text/html\n\n"

debug = 1 
con = None
## should probably get these from the database..
full = float(5622)
empty = float(2240) # AKA "tare" - between 2244 and 2250 seems to be the tare for the air pots
contents = "\"coffee\""
cups_divisor=float(354.8)
try:
	## connect to the database
	con = mdb.connect('localhost', 'coffeeuser', 'coffee16', 'coffeedb');
	cur = con.cursor(mdb.cursors.DictCursor)
	# get scale info from the database
	# how many scales are there? 

	#for each scale, get its reading and display it.
	cur.execute("select id,serialno,scale_name from scales")
	scalerows = cur.fetchall()
	rows=int(cur.rowcount)
	sn=[]
	sid=[]
	sname=[]
	i=0
	for scale in scalerows:
		sn.append(str(scale["serialno"]))
		sid.append(str(scale["id"]))
		sname.append(str(scale["scale_name"]))
		++i
	for i in (0,rows-1):		
		serialno=sn[i]
		scale_id=sid[i]
		scale_name=sname[i]
		## put the readings into columns
		if int(scale_id) & 1: 
			print "<div id=\"right\" >\n"
		else:
			print "<div id=\"left\" >\n"
		print "<center>"+scale_name + "</center>\n<br/>"
		#print "scale id "+ scale_id+" serial: "+ serialno + "\n<br/>"#named: " + scale_name + "\n<br/>"
		# get most recently added reading
		if not cur.execute("select * from readings where reading_time = (select MAX(reading_time) from readings where scale_id = '"+scale_id+"' )"):
			lastreading=0
			if debug: print "no reading found for scale "+ scale_id + "<br/>\n"
		else:
			# this should produce ONE row but in case it does not I'll refer to the rows by their numeric index
			rows = cur.fetchall() # fetchall so we can refer to the columns by name
			reading_time = rows[0]["reading_time"]
			#if debug: print reading_time
			lastreading = float(rows[0]["reading_value"])
			units=rows[0]["reading_units"]	
		
		### calculate fullness
		if lastreading == 0 or lastreading < (empty + 10) :
			print contents + " missing<br />\n"
			pctfull = 0
			pctpx = 0
		elif lastreading == empty :
			print contents + " empty<br />\n"
			pctfull = 0 
			pctpx = 0
		else:
			print str(round(((lastreading-empty)/cups_divisor),1))+" 12 oz cups of "+ contents +"<br />\n"
			print str(lastreading-empty) +"g of "+ contents +"<br />\n"
			#pctfull = (((lastreading-empty) / full)*100)
			pctfull = round((((lastreading-empty) / (full-empty))*100),2)
			print str(pctfull)+"% full<br />\n"
			pctpx = int(500 * ((lastreading-empty) / (full-empty)))
		print """
			<div class="graph">
				<div>
				  <!-- height would be percent times 5 -->
					  <div style="height: 520px;width:1px;" class="barholder"></div>
		"""
		print "			  <div id=\"scale"+scale_id+"\" style=\"height: "+ str(pctpx) +"px;\" class=\"bar\"></div>"
		print """
				</div>
			</div>
		"""
		
		if debug: print "\n<br />reading from database"+"<br />\n"
		if debug: print "most recent reading time: " + str(reading_time) +"<br />\n"
		if debug: print "most recent value : " + str(lastreading) + units +"<br />\n"
		print "<br />\n"
		print "full is " + str(full) + "<br />\n"
		print "empty is " + str(empty) + "<br />\n"
		print "</div>"

except mdb.Error, e:
  
	print "Error %d: %s" % (e.args[0],e.args[1])
	sys.exit(1)
		