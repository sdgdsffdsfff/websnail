import requests
import random
import itertools
import time
import json

class Case3():
	def __init__(self,testsuit,ip='10.10.24.198:8088'):
		self.testsuit = testsuit
		self.custom_timers = {}
		self.case = self.getrandom(testsuit)
		self.path = '?ocr='
		self.url = ''.join(['http://',ip,self.path,self.case.__next__()])
		self.testvalue = True
		self.head = ''
		self.session = requests.Session()

	def getrandom(self,suit):
		ls = itertools.cycle(suit)
		for i in ls:
			yield i

	def test(self):
		r=self.session.get(self.url)
		h=self.session.head(self.url)
		self.head='Server Software: %s' %(h.headers.get('server', 'Unknown'))
		if r.status_code!=200:
			print ('%s ERROR!'%(r.status_code))
			self.testvalue=False
		else:
			print(r.content)

	def run(self):
		nlpdata=self.case.__next__()
		self.custom_timers={}
		r=self.session.get(self.url,timeout=(1.5,5))
		assert r.status_code==200,str(r.status_code)+'error'
		self.custom_timers['c_status']=r.json()['status']

if __name__ == '__main__':
	with open('/home/wenba/xz/automation/data/nlpdata','r') as f:
		suits = [i.strip() for i in f.readlines() if len(i)>1]
	c = Case3(suits)
	c.test()