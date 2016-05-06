#!/usr/bin/python
from . import core,writelog,tracker
import time,json
from multiprocessing import Queue,Process
import sys

def getTestScript(scriptpath,scriptfile):
	try:
		import os,glob
	except Exception as e:
		print ('ERROR: import modules failed')
		sys.exit(1)
	modules={}
	if not os.path.exists(scriptpath):
		print ('ERROR: can not find project')
		sys.exit(1)
	sys.path.append(scriptpath)
	testScript = __import__(scriptfile[:-3])
	return testScript

def getcase(scriptpath,scriptfile,url):
	try:
		testScript = getTestScript(scriptpath,scriptfile)
		c = testScript.Case3(url)
		return c
	except Exception as e:
		print ('ERROR: get case error'+str(e))
		return(None)
		sys.exit(1)

class TestJob(Process):
	def __init__(self,id,c_num,p_num,t_num,run_time,run_num,scriptpath,filename,url,logpath,statusfile,reportfile,controller):
		Process.__init__(self)
		self.id = id
		self.c_num = c_num
		self.p_num = p_num
		self.t_num = t_num
		self.run_time = run_time
		self.run_num = run_num
		self.scriptpath = scriptpath
		self.filename = filename
		self.url = url
		self.logpath = logpath
		self.statusfile = statusfile
		self.reportfile = reportfile
		self.processStatus = {}
		self.controller = controller
		self.queue = Queue()

	def dumpStatus(self,processStatus):
		with open(self.statusfile,'w') as f:
			json.dump(processStatus,f)
			
	def runTest(self):
		print("running test")
		c = getcase(self.scriptpath,self.filename,self.url)
		if c is None:
			return({"id":self.id,"status":"failed","errorinfo":"Error：测试脚本异常！"})
		result = core.test(self.filename,c,self.url)
		return(result)
	
	def run(self):
		c_num = self.p_num*self.t_num
		print('\nConcurrent(autofit): %d, Url: %s, Run_time: %d, Run_loop: %s, Script: %s'%(c_num,self.url,self.run_time,self.run_num,self.filename))
		c = getcase(self.scriptpath,self.filename,self.url)

		process_group=[]

		r = writelog.Writelog(self.queue,self.logpath,False)
		r.daemon=True
		r.start()
	#start
		for i in range(self.p_num):
			p=core.Multi_p(self.queue,i,self.filename,self.t_num,0,self.run_time,self.run_num,c,self.url,self.controller)
			process_group.append(p)
		#print ('start',time.time())
		for g in process_group:
			g.start()
		print('p_num:%s,t_num:%s   all started' %(self.p_num,self.t_num))	

		time.sleep(2)

		start_time = time.time()
		if self.run_time:
			p = tracker.processbar(self.run_time)
			elapsed=0
			while True:
				if self.controller['status'] == -1:
					for p_t in process_group:
						p_t.join()
					self.controller['status'] = -2
					break
				n = r.deadcount
				p.update_time(elapsed)
				self.processStatus = {
					'progress': p.getProgress(),
					"Time":round(elapsed,1),
					'errors':r.error_c,
					'average':round(r.average,3),
					'throught':round(r.throught,2),
					'threads':str(self.p_num*self.t_num-n).ljust(4,' '),
					'status':0
				}
				time.sleep(1)
				self.dumpStatus(self.processStatus)
				sys.stdout.write(chr(27) + '[A' )
				elapsed = time.time() - start_time
				if n == self.p_num*self.t_num:
					break
			print (p)
		elif self.run_num:
			p = tracker.processbar(self.run_num*self.p_num*self.t_num)
			elapsed=0
			while True:
				if self.controller['status'] == -1:
					for p_t in process_group:
						p_t.join()
					self.controller['status'] = -2
					break
				p.update_time(r.total_c)
				elapsed = time.time() - start_time
				self.processStatus = {
					"progress": p.getProgress(),
					'TotalRequest':r.total_c,
					"errors":r.error_c,
					"average":round(r.average,3),
					"throught":round(r.throught,2),
					"threads":str(self.p_num*self.t_num-r.deadcount).ljust(4,' '),
					"status":0
					}
				print(self.processStatus)
				self.dumpStatus(self.processStatus)
				sys.stdout.write(chr(27) + '[A' )
				if r.total_c == self.run_num*self.p_num*self.t_num:
					break
				time.sleep(1)
			print (p)

		for g in process_group:
			g.join()
		while not self.queue.empty():
			print('\n\nanalyzing results...\n')
			sys.stdout.write(chr(27) + '[A' )
			time.sleep(1)
		print('\nanalyzing results...\n')
		print('r.logpath:',r.logpath)
		report = tracker.Report(self.id,r.logpath,self.url,self.reportfile)
		report.generateReport()
		self.processStatus['status'] = 1
		print('processStatus:%s' %self.processStatus)
		self.dumpStatus(self.processStatus)
	
if __name__ == '__main__':
	pass
	#logpath = '/home/chao.chen/automation/websnail/logs/'
	#testJob = TestJob(1,100,1,102,0,1,'ocr.py','10.2.1.38:8089',logpath)
	#print(testJob)
	#testJob.run()


