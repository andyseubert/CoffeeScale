#!/usr/bin/env python
import sys
if len(sys.argv) == 1:sys.exit(1)
from twython import Twython
import sqlite3 as lite
con = None
# get creds from database
try:
	con = lite.connect('/usr/local/CoffeeScale/c16')
	cur=con.cursor()
	cur.execute("SELECT setting_value,setting_name FROM settings WHERE setting_name like '%twitter%'")
	rows=cur.fetchall()
	for row in rows:
		if str(row[1])=="twitter_CONSUMER_KEY"   : c_key=str(row[0])
		if str(row[1])=="twitter_CONSUMER_SECRET": c_secret=str(row[0])
		if str(row[1])=="twitter_ACCESS_KEY"     : a_key=str(row[0])
		if str(row[1])=="twitter_ACCESS_SECRET"  : a_secret=str(row[0])
	
except lite.Error,e:
	print "Error %s:" % e.args[0]
	sys.exit(1)
    
finally:    
	if con:
		con.close()

##### THIS WILL UPDATE STATUS
twitter = Twython(c_key,c_secret,a_key,a_secret)
if sys.argv[1] == "img":
	photo= open (sys.argv[2],'rb')
	twitter.update_status_with_media(status=sys.argv[3], media=photo)
else:
	twitter.update_status(status=sys.argv[1])

######
## only need this if asking to authorize this app to post on behalf of someone else		
# twitter = Twython(c_key, c_secret)
# auth = twitter.get_authentication_tokens()
# print auth
# OAUTH_TOKEN = auth['oauth_token']
# OAUTH_TOKEN_SECRET = auth['oauth_token_secret']
# AUTH_URL = auth['auth_url']
# print ("follow this URL and return with pin " + AUTH_URL)
# PIN = raw_input("PIN: ")
# twitter = Twython(KEY, SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
# final_step = twitter.get_authorized_tokens(PIN)
# save these:
# OAUTH_TOKEN = final_step['oauth_token']
# OAUTH_TOKEN_SECERT = final_step['oauth_token_secret']
# print "OAUTH_TOKEN = "+final_step['oauth_token']
# print "OAUTH_TOKEN_SECERT = "+final_step['oauth_token_secret']
######
