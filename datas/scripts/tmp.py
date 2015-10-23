import requests
import random
import itertools
import os

dataset = '/data/websnail/resources/imgs'
lis = [os.path.join(root,s) for root,firs,files, in os.walk(dataset) for s in files]

class Case3():
	def __init__(self,testsuit,ip='10.2.1.38:8089'):
		self.custom_timers = {}
		self.path = '/'
		self.url = ''.join(['http://',ip,self.path])
		self.testvalue = True
		self.head = ''
		self.session = requests.Session()
		if testsuit:
			self.case = self.getrandom(testsuit)
		else:
			self.case = self.getrandom(lis)
	def getrandom(self,suit):
		ls = itertools.cycle(suit)
		for i in ls:
			yield i

	def test(self):
		img = self.case.__next__()
		r = self.session.post(self.url,files={'file':open(img,'rb')},timeout=(1.5,16.5))
		h = self.session.head(self.url)
		self.head = 'Server Software: %s' %(h.headers.get('server', 'Unknown'))
		if r.status_code != 200:
			print ('%s ERROR!'%(r.status_code))
			self.testvalue = False
			return
		else:
			print(r.content)

	def run(self):
		self.custom_timers = {}
		img = self.case.__next__()
		self.custom_timers['img'] = img
		r = self.session.post(self.url,files={'file':open(img,'rb')},timeout=(1.5,16.5))
		assert r.status_code == 200,str(r.status_code) + 'error'
		self.custom_timers['c_status'] = r.json()['status']
		self.custom_timers['t_recogtime'] = r.json()['recogtime']
		self.custom_timers['t_layouttime'] = r.json()['layouttime']

if __name__=='__main__':
	c = Case3([])
	c.test()
	#print(c.custom_timers)
