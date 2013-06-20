import requests
import time
__author__ = 'grace'
i=0
while True:
    requests.get("http://115.68.24.230/test.php")
    i+=1
    print i
    time.sleep(1)