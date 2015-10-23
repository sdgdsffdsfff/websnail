import requests,random,itertools,time,json
from collections import OrderedDict

f=open('/home/wenba/xz/automation/data/ocrdatafile','r')
ocrdatas=f.read()
ocrdatas=ocrdatas.split('\n')

class Case3():
	def __init__(self,testsuit=None,ip='10.10.1.151:8081'):
		self.custom_timers = OrderedDict()
		self.path = '/search/query'
		self.url = ''.join(['http://',ip,self.path])
		self.testvalue = True
		self.head = ''
		self.session = requests.Session()
		if testsuit:
			self.m = self.getrandom(testsuit)
		else:
			self.m = self.getrandom(ocrdatas)
	
	def getrandom(self,datas):
		cs = itertools.cycle(datas)
		for i in cs:
			yield i

	def test(self):
		data = self.m.__next__()
		r = self.session.post(self.url,data={"keywords":data,"limit":5},timeout=(1.5,5.0))
		h = self.session.head(self.url)
		self.head = 'Server Software: %s' %(h.headers.get('server', 'Unknown'))
		if r.status_code != 200:
			print ('%s ERROR!'%(r.status_code))
			self.testvalue=False
		else:
			print('状态码：%s' %r.status_code)

	def run(self):
		data = self.m.__next__()
		self.custom_timers['key'] = data
		r = self.session.post(self.url,data={"keywords":data,"limit":5},timeout=(1.5,5.0))
		assert r.status_code == 200,str(r.status_code)+'error'
		self.custom_timers['c_type']=r.json()['type']

if __name__ == "__main__":
	c = Case3()
	c.test()