from threading import Thread
from states import snail_stat
import time

def runJob():
	while 1:
		snail_stat.total_requests += 1
		time.sleep(1)

for i in range(10):
	t = Thread(target=runJob,args=())
#t.setDaemon(True)
	t.start()

while 1:
	time.sleep(1)
	print(snail_stat.total_requests)
	
