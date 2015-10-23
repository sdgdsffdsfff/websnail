import requests
from collections import OrderedDict
import itertools,json

class Case3():
	def __init__(self,testsuit,ip='10.2.1.63'):
		self.testsuit = self.getrandom(testsuit)
		self.custom_timers = OrderedDict()
		self.path = '/getSubject'
		self.url = ''.join(['http://',ip,self.path])
		self.testvalue = True
		self.head = ''
		self.session = requests.Session()

	def getrandom(self,testsuit):
		ls = itertools.cycle(testsuit)
		for i in ls:
			yield i

	def test(self):
		data = self.testsuit.__next__()
		r = self.session.post(self.url,data=data,timeout=(3.0,5.0))
		#h = self.session.head(self.url)
		#self.head = 'Server Software: %s' %(h.headers.get('server', 'Unknown'))
		if r.status_code != 200:
			print ('%s ERROR!'%(r.status_code))
			self.testvalue=False
		else:
			print('状态码：%s' %r.text)

	def run(self):
		data = self.testsuit.__next__()
		r = self.session.post(self.url,data=data,timeout=(3.0,5.0))
		h = self.session.head(self.url)
		self.head = 'Server Software: %s' %(h.headers.get('server', 'Unknown'))
		assert r.status_code == 200,str(r.status_code)+'error'
		print(r.text)

if __name__ == "__main__":
	import pickle
	suits = pickle.load(open('/home/chao.chen/automation/websnail/datas/suitfiles/sourcefile/b.pkl','rb'))
	c = Case3(suits)
	c.run()
