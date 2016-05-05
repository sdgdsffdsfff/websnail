import requests,itertools,random
from collections import OrderedDict

lis = []
class Case3():
	def __init__(self,testsuit,ip='121.43.101.211:8180'):
		self.custom_timers = OrderedDict()
		self.path = '/suime-user/student/login'
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
		data = {
			"cellphone":18516042356,
			"password":"6547436690a26a399603a7096e876a2d"
		}
		r = self.session.post(self.url,data=data,headers={},timeout=(5.0,10.0))
		if r.status_code != 200:
			print ('%s ERROR!'%(r.text))
			self.testvalue=False
		else:
			print('状态码：%s' %r.status_code)

	def run(self):
		data = {
			"cellphone":18516042356,
			"password":"6547436690a26a399603a7096e876a2d"
		}
		r = self.session.post(self.url,data=data,headers={},timeout=(5.0,10.0))
		assert r.status_code == 200,str(r.status_code)+'error'
		

if __name__ == "__main__":
	c = Case3([])
	c.run()