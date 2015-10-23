from queue import Queue
#import Queue
from threading import Thread
from collections import Counter
import time
import os

class Writelog(Thread):
	def __init__(self,queue,output_dir,logturn):
		Thread.__init__(self)
		self.queue=queue
		self.output_dir=output_dir
		try:
			if not os.path.isdir(self.output_dir):
				os.makedirs(self.output_dir)
		except Exception as e:
			print ('ERROR: Can not create result directory\n')
			sys.exit(1)
		self.total_c=0
		self.error_c=0
		self.uncheck_c=0
		self.average=0
		self.throught=0
		self.elapsed=0
		self.all_time=0
		self.logpath=''
		self.deadcount=0
	def run(self):
		self.logpath = ''.join([self.output_dir,os.sep,time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime(time.time()))+".log"])
		with open(self.logpath,'w') as f:
			while True:
				try:
					elapsed, pt_name, span ,error, custom_timers=self.queue.get(False)
					self.total_c+=1
					if error:
						self.error_c+=1
						custom_timers['error']=error
					self.uncheck_c=self.queue.qsize()
					f.write("%i, %.3f, %s, %.2f, %i, %i, %s\n"%(self.total_c, elapsed ,pt_name, span,self.error_c,self.uncheck_c,custom_timers))
					f.flush()
					if pt_name.startswith('dead'):
						self.deadcount+=1
					#self.uncheck_c=self.queue.qsize()
					self.all_time+=span
					self.elapsed=elapsed
					self.average=self.all_time/self.total_c
					self.throught=self.total_c/elapsed
				except Exception as e:
					time.sleep(.05)
					#print (e)
