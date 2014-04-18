#!/usr/bin/python

## can I sms?
## have I sent an sms in the last 5 minutes to a particular recipient regarding this event for this scale?

## inputs:
##  eventType
##  recipient
##  scale_id


import sqlite3 as lite
import os
import sys
import subprocess
import time as t
from datetime import datetime
from dateutil import parser

def main(scale_id,eventType,recipient):
    #if len(sys.argv) < 3:
    #    print "not enough args"
    #    exit(1)
    #scale_id  = sys.argv[0]
    #eventType = sys.argv[1]
    #recipient = str(sys.argv[2])
    
    con = lite.connect('/usr/local/CoffeeScale/c16')
    con.text_factory = str
    con.row_factory = lite.Row
    cur=con.cursor()
    cur.execute("select MAX(sms_time) as lastsms FROM texts WHERE scale_id=? AND type =? AND recipient=?",(scale_id,eventType,recipient))
    row=cur.fetchone()
    if str(row[0]) == "None": ## first sms ever
        print "Yes"
        return True
    else :
            then = parser.parse(row[0])
            if debug: print "last sms to _recipient_ for "+scale_name+" was "+ str(round( (now - then ).total_seconds() / 60)) +" minutes ago"
### if the last tweet was more than one x ago:
            if round( (now - then ).total_seconds() / 60) > 30:
                print "Yes"
                return True
    print "No"
    return False

if __name__ == "__main__":
    main()
