from multiprocessing import Process
import threading
import time
import sys
import queue
modules={}

def test(scriptfile,case,ip):
	if case != None:
		print("case is not None")
		c = case
	else:
		module_name = script_init(scriptfile)
		try:
			c = modules[module_name].Case3(ip)
		except Exception as e:
			print ('ERROR: can not find test script: %s.'%(scriptfile))
			#sys.exit(1)
			return({'status':'failed','errorinfo':'Can not find test script:%s' %scriptfile})
	try:
		c.test()
	except Exception as e:
		print (e)
		return({'status':'failed','errorinfo':'脚本Case3.test()执行异常，请检查脚本！'})
	if c.testvalue:
		print ('check pass!')
		return({'status':'success','url':c.url})

class Multi_p(Process):
	def __init__(self,queue,p_name,scriptfile,thread_num,rampup,run_time,run_num,case,ip,controller):
		Process.__init__(self)
		self.queue=queue
		self.p_name=p_name
		self.scriptfile=scriptfile
		self.thread_num=thread_num
		self.rampup=rampup
		self.run_time=run_time
		self.run_num=run_num
		self.start_time=time.time()
		self.case=case
		self.ip=ip
		self.controller = controller

	def run(self):
		ts=[]
		for i in range(int(self.thread_num)):
			#spacing=float(self.rampup)/float(self.thread_num)
			#if spacing:
				#time.sleep(spacing)
			t=Multi_t(self.queue,self.p_name,i,self.start_time,self.scriptfile,self.run_time,self.run_num,self.case,self.ip,self.controller)
			t.setDaemon=True
			ts.append(t)
			t.start()
		for t in ts:
			t.join()
		#print ("%s end %s"%(self.p_name,time.time()))
	#def getcurrent(self):
		#return len(threading.enumerate()) 
class Multi_t(threading.Thread):
	def __init__(self,queue,p_name,t_name,start_time,scriptfile,run_time,run_num,case,ip,controller):
		threading.Thread.__init__(self)
		self.queue=queue
		self.pt_name='%s-%s'%(p_name,t_name)
		self.start_time=start_time
		self.scriptfile=scriptfile
		self.run_time=run_time
		self.run_num=run_num
		self.default_timer=time.time
		self.case=case
		self.ip=ip
		self.controller = controller

	def run(self):
		if self.case!=None:
			c=self.case
		else:
			#print ('none')
			module_name=script_init(self.scriptfile)
			#print (module_name)
			try:
				c=modules[module_name].Case3(self.ip)
				#print ('case is start')
				#c=eval(module_name+'.Case3()')
				#print ('case is None')
			except Exception as e:
				print (str(e))
				print ('ERROR: can not find test script: %s.'%(self.scriptfile))
				return
		elapsed=0
		c.custom_timers={}
		if self.run_time:
			while True:
				if self.controller['status'] == 2:
					time.sleep(5)
					self.run_time += 5
					continue
				if self.controller['status'] == -1:
					break
				error=''
				start=self.default_timer()
				try:
					c.run()
				except Exception as e:
					error=str(e).replace(',','')
					#print (error)
				finally:
					span=self.default_timer()-start
				elapsed=time.time()-self.start_time
				if elapsed>self.run_time:
					fields=(elapsed,'dead', span,error,c.custom_timers)
					self.queue.put(fields)
					break
				else:
					fields=(elapsed,self.pt_name, span,error,c.custom_timers)
					self.queue.put(fields)
		elif self.run_num:
			elapsed_num=0
			while True:
				if self.controller['status'] == 2:
					time.sleep(5)
					continue
				if self.controller['status'] == -1:
					break
				error=''
				start=time.time()
				try:
					c.run()
				except Exception as e:
					error=str(e).replace(',','')
				finally:
					span=self.default_timer()-start
				elapsed=time.time()-self.start_time
				elapsed_num+=1
				#print('this.will.appear')
				if elapsed_num ==self.run_num:
					fields=(elapsed,'dead',span,error,c.custom_timers)
					self.queue.put(fields)
					break
				else:
					fields=(elapsed,self.pt_name,span,error,c.custom_timers)
					self.queue.put(fields)
			return
		else:
			print ('ERROR: nothing')

def script_init(scriptfile):
	if scriptfile.lower().endswith('.py'):
		module_name=scriptfile.replace('.py','')
	else:
		print ('ERROR: scripts must have .py extension. can not run test script: %s.' % (scriptfile))
		sys.exit(1)
	return module_name

