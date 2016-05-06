import requests,itertools,random
from collections import OrderedDict

class Case3():
	def __init__(self,url='http://121.43.101.211:8180/suime-user/student/login'):
		self.custom_timers = OrderedDict()
		self.url = url
		self.testvalue = True

	def test(self):
		data = {
			"cellphone":18516042356,
			"password":"6547436690a26a399603a7096e876a2d"
		}
		r = requests.post(self.url,data=data,headers={},timeout=(5.0,10.0))
		if r.status_code != 200:
			print ('%s ERROR!'%(r.status_code))
			self.testvalue=False
		else:
			print('状态码：%s' %r.status_code)

	def run(self):
		data = {
			"cellphone":18516042356,
			"password":"6547436690a26a399603a7096e876a2d"
		}
		r = requests.post(self.url,data=data,headers={},timeout=(5.0,10.0))
		assert r.status_code == 200,str(r.status_code)+'error'
		self.custom_timers['result']=r.json()['result']
		

if __name__ == "__main__":
	c = Case3()
	c.test()