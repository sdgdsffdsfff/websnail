import requests
import random
import itertools
import time
import json

class Case3():
	def __init__(self,testsuit=None,ip='10.2.1.66'):
		self.testsuit = testsuit
		self.custom_timers={}
		self.path='/instructor/action/beassigned'
		self.url=''.join(['http://',ip,self.path])
		self.testvalue=True
		self.head=''
		self.session=requests.Session()

	def randOrderNo(self):
		return random.randint(1,100000000000)

	def randInstrucId(self):
		ids = [random.randint(1,100000000) for i in range(4)]
		return ids

	def test(self):
		data = {"orderNo":self.randOrderNo(),"instructorIds":self.randInstrucId(),"datetime":"1020290390"}
		r=self.session.post(self.url,data=json.dumps(data),timeout=(1.5,5))
		h=self.session.head(self.url)
		self.head='Server Software: %s' %(h.headers.get('server', 'Unknown'))
		if r.status_code!=200 and r.json()['status'] != -1:
			print ('%s ERROR!'%(r.status_code))
			self.testvalue=False
		else:
			print(r.text)

	def run(self):
		data={"orderNo":self.randOrderNo(),"instructorIds":self.randInstrucId(),"datetime":"1020290390"}
		self.custom_timers={}
		r=self.session.post(self.url,data=json.dumps(data),timeout=(1.5,5))
		assert r.status_code==200,str(r.status_code)+'error'
		self.custom_timers['c_status']=r.json()['status']


if __name__ == "__main__":

	c = Case3()
	c.test()









