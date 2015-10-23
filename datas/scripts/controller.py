import requests,os,itertools,random
from collections import OrderedDict

dataset='/data/imgs/olimg0203'
lis=[os.path.join(root,s) for root,dirs,files in os.walk(dataset) for s in files]

class Case3():
	def __init__(self,testsuit=None,ip='10.10.30.56:9090'):
		self.custom_timers = OrderedDict()
		self.path = '/wenba-scheduler/query'
		self.url = ''.join(['http://',ip,self.path])
		self.testvalue = True
		self.head = ''
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
		data = {
			'uid':random.randint(501,1000),
			'fid':random.randint(10000,99999)
		}
		r = requests.post(self.url,data=data,files={"file": open(img, 'rb')},timeout=(3.0,30.0))
		h = requests.head(self.url)
		self.head = 'Server Software: %s' %(h.headers.get('server', 'Unknown'))
		if r.status_code != 200:
			print ('%s ERROR!'%(r.status_code))
			self.testvalue=False
		else:
			print('状态码：%s' %r.status_code)

	def run(self):
		img = self.case.__next__()
		data = {
			'uid':random.randint(501,1000),
			'fid':random.randint(10000,99999)
		}
		r = requests.post(self.url,data=data,files={"file": open(img, 'rb')},timeout=(3.0,30.0))
		assert r.status_code == 200,str(r.status_code)+'error'
		self.custom_timers['c_type']=r.json()['type']
		self.custom_timers['c_server_status']='%s,%s'%(r.json()['serverType'],r.json()['statusCode'])
		
if __name__ == "__main__":
	c = Case3([])
	c.run()
	print(c.custom_timers)