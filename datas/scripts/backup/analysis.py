import requests
from collections import OrderedDict

class Case3():
	def __init__(self,testsuit=None,ip='10.2.1.68'):
		self.testsuit = testsuit
		self.custom_timers = OrderedDict()
		self.path = '/analysis'
		self.url = ''.join(['http://',ip,self.path])
		self.testvalue = True
		self.head = ''
		self.session = requests.Session()

	def test(self):
		data = {
			"type":"OCR",
			"conc":10,
			"suit":"OCR_suit01"
		}
		r = self.session.get(self.url,params=data,headers={'content-type': 'text/html'},timeout=(30,60))
		h = self.session.head(self.url)
		self.head = 'Server Software: %s' %(h.headers.get('server', 'Unknown'))
		if r.status_code != 200:
			print ('%s ERROR!'%(r.status_code))
			self.testvalue=False
		else:
			#print(r.text)
			print('test ok!')

	def run(self):
		data = {
			"type":"OCR",
			"conc":500,
			"suit":"OCR_01"
		}
		r = self.session.post(self.url,params=data,headers={'content-type': 'text/html'},timeout=(30,60))
		assert r.status_code == 200,str(r.status_code)+'error'
		


if __name__ == "__main__":
	c = Case3()
	c.test()
