import requests
import json
import random
import schedule 
import time

def job():
   solditems = requests.get('http://dojodevopschallenge.s3-website-eu-west-1.amazonaws.com/fortune_of_the_day.json')
   data = solditems.json()
   output=random.choice(data)
   html = output["message"]
   f = open('index.html','w')

   message = """<html>
   <head>OUTPUT MESSAGE</head>
   <body><p>"""+str(html)+"""</p></body>
   </html>"""

   f.write(message)
   f.close()

schedule.every(20).seconds.do(job)
while 1:
    schedule.run_pending()
    time.sleep(1)
