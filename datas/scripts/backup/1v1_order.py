import requests
import random
import itertools
import time
import json

class Case3():
	def __init__(self,testsuit=None,ip='10.2.1.100:8000'):
		self.testsuit = testsuit
		self.custom_timers={}
		self.path='/order/action/create'
		self.url=''.join(['http://',ip,self.path])
		self.testvalue=True
		self.head=''
		self.session=requests.Session()


	def test(self):
		headers = {"content-type":"application/json"}
		data = {"orderNo": 2005, "uid": 2001, "thumb": "http://www.baidu.com/1.png", "aid": 1111,"createTime": 1470000001,"subject": 2,"term": 7}
		r=self.session.post(self.url,data=json.dumps(data),headers=None,timeout=(1.5,5))
		h=self.session.head(self.url)
		self.head='Server Software: %s' %(h.headers.get('server', 'Unknown'))
		if r.status_code!=200 and r.json()['status'] != 0:
			print ('%s ERROR!'%(r.status_code))
			self.testvalue=False
		else:
			print('test ok!')

	def run(self):
		data = {"orderNo": 2005, "uid": 2001, "thumb": "http://www.baidu.com/1.png", "aid": 1111,"createTime": 1470000001,"subject": 2,"term": 7}
		self.custom_timers={}
		r=self.session.post(self.url,data=json.dumps(data),timeout=(1.5,5))
		assert r.status_code==200,str(r.status_code)+'error'
		self.custom_timers['c_status']=r.json()['status']


if __name__ == "__main__":

	c = Case3()
	c.test()









