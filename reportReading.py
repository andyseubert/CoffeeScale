#!/usr/bin/python

# this reports the latest scale reading so the web page can grab it

import sqlite3 as lite
import os
import sys
import shutil
import time as t
from datetime import datetime
import dateutil.parser as parser
import subprocess

debug = 0
con = None
## should probably get these from the database..
full = float(5680)
empty = float(2240) # AKA "tare" - between 2244 and 2250 seems to be the tare for the air pots
contents = "coffee"
cups_divisor=float(354.8)
cups="0"
temphtml="/tmp/index.html" #<-- write to temp file then copy over index file. Should make it better
indexhtml="/usr/local/CoffeeScale/index.html"
indexpath="/usr/local/CoffeeScale/"

pagehead = """
<html>
	<head>
		<title>COFFEE FOREVER</title>
		
		<!-- Meta tags -->
		<meta http-equiv="refresh" content="15">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<meta http-equiv="X-UA-Compatible" content="IE=edge">

		<!-- Bootstrap -->
		<link href="css/bootstrap.min.css" rel="stylesheet">

		<!-- Custom Styles-->
		<link href="css/omg-coffee.css" rel="stylesheet">
		
		<!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
		<!--[if lt IE 9]>
			<script src="js/html5.js"></script>
			<script src="js/respond.min.js"></script>
		<![endif]-->
</head>
<body>
<div class="container">
		<div class="row">
			<div class="col-md-12">				
	<div id="status">
 
"""

while 1:
	#t.sleep(2)
	now = datetime.now()
	file=open(temphtml,'w')
	file.write(pagehead)
	## connect to the database
	con = lite.connect('/usr/local/CoffeeScale/c16')
	con.text_factory = str
	con.row_factory = lite.Row
	cur=con.cursor()

	# get scale info from the database
	# how many scales are there? 

	#for each scale, get its reading and display it.
	cur.execute("select id,serialno,scale_name from scales")
	scalerows = cur.fetchall()
	rows=len(scalerows)
	sn=[]
	sid=[]
	sname=[]
	for scale in scalerows:
		sn.append(str(scale["serialno"]))
		sid.append(str(scale["id"]))
		sname.append(str(scale["scale_name"]))
	for i in xrange(rows):
		lastreading=0
		pctfull=0
		cups="0"
		serialno=sn[i]
		scale_id=sid[i]
		scale_name=sname[i]
		## make a temp file for each scale to put html into for the twittering
		scaletmpfilename=str(scale_id)+".html"
		scaletmpfile=open("/tmp/"+scaletmpfilename,'w')
		scaletmpfile.write(pagehead)
		
		if not cur.execute("select * from (select reading_value,reading_units, scale_id, MAX(reading_time) as reading_time from readings where scale_id = "+scale_id+" ) "):
			lastreading=0
			if debug:
				file.write ( "no reading found for scale "+ scale_id + "<br/>\n" )
				scaletmpfile.write ( "no reading found for scale "+ scale_id + "<br/>\n" )
		else:
			# this should produce ONE row 
			rows = cur.fetchone() 
			reading_time = str(rows["reading_time"])
			lastreading = float(rows["reading_value"])
			units=rows["reading_units"]	
		cur.execute("select MAX(fulltime) as lastrefill FROM (select reading_time as fulltime,reading_value,scale_id from readings where reading_value >= 5622 AND reading_value <= 5900 AND scale_id = '"+scale_id+"') xo")
		row = cur.fetchone()
		last_fulltime=str(row["lastrefill"])
		### calculate fullness
		if int(lastreading) == 0 or int(lastreading) < (empty + 10) :
			now = datetime.now()
			then = parser.parse(reading_time)
			td=round( (now - then ).total_seconds() / 60)
			if td > 10:
				emptytime = "It has been "+str(td)+" minutes at zero<br/>\n"
			contentsmsg = contents + " missing\n" 
			pctfull = 0
		elif lastreading == empty :
			contentsmsg = contents + " empty<br />\n" 
			pctfull = 0 
		else:
			emptytime=""
			pctfull = str(round((((lastreading-empty) / (full-empty))*100),2))
			cups = str(round(((lastreading-empty)/cups_divisor),1))
			oz = str( round(((lastreading-empty)*.035274),1))
			contentsmsg  = "					"+oz+" ounces of "+contents+" remain<br>"
			contentsmsg += "					"+str(pctfull)+"% full<br>"
		file.write ( """

				<div class="row">
					<div class="col-md-4">
						<div class="panel panel-info">
		""" )
		file.write ( "				<div class=\"panel-heading\">"+scale_name+"</div>" )
		file.write ( "				<div class=\"panel-body\">" )
		file.write ( contentsmsg )
		file.write ( "					<div class=\"coffee-wrap\">" )
		file.write ( "					<span class=\"coffee-icon glyphicon glyphicon-tint\"></span>" )
		file.write ( "					<div class=\"coffee-bar\" style=\"height: "+str(pctfull)+"%;\"></div>" )
		file.write ( "					</div>" )
		file.write ( "				</div>" )
		file.write ( " 			<div class=\"panel-footer\">" )
#		file.write ( "					last changed at "+str(reading_time)+"<br>" )
		file.write ( "					current scale reading:"+str(lastreading)+"g<br>" )
#		file.write ( "					last refill time :"+str(last_fulltime)+"<br>" )
		file.write ( "					this page last updated :"+str(now.strftime("%I:%M%p on %B %d, %Y"))+"<br>" )
		if debug:
			file.write ( "				reading from database<br>" )
			file.write ( " 			most recent reading time: "+str(reading_time)+"<br>" )
			file.write ( "				most recent value : "+str(lastreading)+"<br>" )
			file.write ( " 			<strong>full is "+str(full)+"<br>" )
			file.write ( " 			empty is "+str(empty)+"</strong><br>" )
			file.write ( "				"+str(lastreading-empty)+"g of "+contents+"<br>" )
			file.write ( "              "+serialno+"<br/>" )
		file.write ( """
							</div>
						</div>
					</div>
		""" )
		## single scale result file 
		scaletmpfile.write ( """

				<div class="row">
					<div class="col-md-4">
						<div class="panel panel-info">
		""" )
		scaletmpfile.write ( "				<div class=\"panel-heading\">"+scale_name+"</div>" )
		scaletmpfile.write ( "				<div class=\"panel-body\">" )
		scaletmpfile.write ( contentsmsg )
		scaletmpfile.write ( "					<div class=\"coffee-wrap\">" )
		scaletmpfile.write ( "					<span class=\"coffee-icon glyphicon glyphicon-tint\"></span>" )
		scaletmpfile.write ( "					<div class=\"coffee-bar\" style=\"height: "+str(pctfull)+"%;\"></div>" )
		scaletmpfile.write ( "					</div>" )
		scaletmpfile.write ( "				</div>" )
		scaletmpfile.write ( " 			<div class=\"panel-footer\">" )
		if debug:
			scaletmpfile.write ( "				reading from database<br>" )
			scaletmpfile.write ( " 			most recent reading time: "+str(reading_time)+"<br>" )
			scaletmpfile.write ( "				most recent value : "+str(lastreading)+"<br>" )
			scaletmpfile.write ( " 			<strong>full is "+str(full)+"<br>" )
			scaletmpfile.write ( " 			empty is "+str(empty)+"</strong><br>" )
			scaletmpfile.write ( "				"+str(lastreading-empty)+"g of "+contents+"<br>" )
			scaletmpfile.write ( "              "+serialno+"<br/>" )
		scaletmpfile.write ( """
							</div>
						</div>
					</div>
		""" )
		### close single scale report file here		
		scaletmpfile.write ( """
			</div>
		</div>
		</div>
		</div>
	
		</body>
		</html>
		""")
		scaletmpfile.close()
		## copy single scale report
		shutil.copyfile("/tmp/"+scaletmpfilename,indexpath+scaletmpfilename)
		shebang="/usr/local/CoffeeScale/webkit2png -x 800 600 --scale=600 550 -o "+scale_id+".png http://localhost/"+scale_id+".html"
		cmd=shebang.split()
		subprocess.call(["/usr/local/CoffeeScale/webkit2png","-x","800","600","--scale","600","550","-o",scale_id+".png","http://localhost/"+scale_id+".html"])

	### close all scale file here	
	file.write ( """
		</div>
		<a href=http://knowledge25.collegenet.com/display/~andys/raspberry+coffee>http://knowledge25.collegenet.com/display/~andys/raspberry+coffee</a>
		
	</div>
	</div>
	</div>

	</body>
	</html>
	""")

	file.close()
	con.close()
## copy temp html on to real html
	shutil.copyfile(temphtml,indexhtml)