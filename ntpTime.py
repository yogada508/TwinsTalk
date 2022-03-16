import os 
import time 
import ntplib 
c = ntplib.NTPClient() 
response = c.request('192.168.1.160') 
ts = response.tx_time

_date = time.strftime('%Y-%m-%d',time.localtime(ts)) 
_time = time.strftime('%X',time.localtime(ts)) 
print(_date,_time,time.time()-ts)
#os.system('date {} && time {}'.format(_date,_time)) 