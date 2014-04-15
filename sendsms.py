#!/usr/bin/python
import smtplib
import sys
server = smtplib.SMTP( "smtp.gmail.com", 587 )
server.starttls()
server.login( 'cncoffeeon16@gmail.com', 'coffeepoton16.$L@P' )
server.sendmail( 'coffeepoton16', '5035228381@vtext.com', str(sys.argv[1]) )
