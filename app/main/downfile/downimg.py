from multiprocessing import Process
import threading,os.path,queue,requests
from datetime import datetime

class Multi_p(Process):
	def __init__(self,p_name,que,savedir,thread_num,logdir):
		Process.__init__(self)
		self.p_name=p_name
		self.que=que
		self.savedir = savedir
		self.thread_num = thread_num
		self.logdir = logdir

	def run(self):
		threads = []
		for i in range(self.thread_num):
			t = Multi_t(self.p_name,
						self.que,
						i,
						self.savedir,
						self.logdir
				)

			t.setDaemon = True
			threads.append(t)
			t.start()

		for t in threads:
			t.join()

class Multi_t(threading.Thread):
	def __init__(self,p_name,que,t_name,savedir,logdir):
		threading.Thread.__init__(self)
		self.que = que
		self.pt_name = '{p_name}-{t_name}'.format(p_name=p_name,t_name=t_name)
		self.savedir = savedir
		self.logdir = logdir

	def run(self):
		while True:
			url = ''
			try:
				url = self.que.get(False)
				r = requests.get(url)
				if r.status_code != 200:
					self.logging('failed',url)
					continue
			except queue.Empty:
				self.logging('done',"finished at:"+datetime.now().strftime('%Y_%m_%d-%H_%M_%S'))

				break
			except Exception as e:
				print(e)
				self.logging('failed',url)
				continue

			filename = os.path.join(self.savedir,url.split('com/')[1])

			if os.path.isfile(filename):
				self.logging('exists',url)
				continue
			size = int(r.headers['content-length'])
			try:
				with open(filename,'wb') as f:
					f.write(r.content)
			except OSError:
				print('磁盘空间不足')
				return
			with open(filename,'rb') as f:
				filesize = len(f.read())
				if filesize != size:
					self.logging('failed',url)
	
	def logging(self,type,url):
		logname = os.path.join(self.logdir,type)
		if not os.path.isdir(self.logdir):
			os.mkdir(self.logdir)

		with open(logname,'a') as f:
			f.write(url+'\n')

class DownImgJob(object):
	
	def __init__(self,que,savedir,p_num,t_num,logdir):
		self.que = que
		self.savedir = savedir
		self.p_num = p_num
		self.t_num = t_num
		self.logdir = logdir
	
	def run(self):
		
		p_group = []
		
		for i in range(self.p_num):
			p = Multi_p(i,self.que,self.savedir,self.t_num,self.logdir)
			p.start()
			print("{0}process has started".format(i))
			p_group.append(p)
		
		for progress in p_group:
			progress.join()


if __name__ == "__main__":
	print('ok')
