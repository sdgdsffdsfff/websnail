import requests,base64,random,json,itertools,threading
from collections import OrderedDict

keys = range(20150830004363,20150830999999)

class safe_generator:  
    def __init__(self, gen):  
        self.gen = gen  
        self.lock = threading.Lock()  
  
    def __iter__(self):  
        return self.__next__()  
  
    def next(self):  
        with self.lock:  
            return self.gen.__next__()  

class Case3():
	def __init__(self,testsuit=None,ip='10.2.1.44:18080'):
		self.testsuit = testsuit
		self.keys = safe_generator(self.getkey(keys))
		self.key = self.keys.next()
		self.ip = ip
		self.path = '/actionByOrderId/'
		self.url = ''.join(['http://',ip,self.path+self.key])
		self.custom_timers = OrderedDict()
		self.testvalue = True
		self.head = ''
		self.session = requests.Session()

	def getkey(self,keys):
		cs = itertools.cycle(keys)
		for i in cs:
			yield str(i)

	def test(self):
		key = self.keys.next()
		self.url = ''.join(['http://',self.ip,self.path+key])
		b64_key = base64.b64encode(key.encode())
		data = {
			"Row":[{"key":b64_key.decode(),
			"Cell":[{"column":"c3R1ZGVudDpvcmRlck5v",
			"$":"IjIwMTUwODMwMDA0MzYzIg=="},
			{"column":"c3R1ZGVudDphY3Rpb24=",
			"$":"IjQwMiI="},
			{"column":"c3R1ZGVudDp1aWQ=",
			"$":"IjEyMzQ1Ig=="},
			{"column":"c3R1ZGVudDpkYXRldGltZQ==",
			"$":"IjE0NDA5NTAzODgi"}]}]
		}
		r = self.session.post(self.url,data=json.dumps(data),headers={'content-type':'application/json','accept':'application/json'},timeout=(2,5))
		h = self.session.head(self.url)
		self.head = 'Server Software: %s' %(h.headers.get('server', 'Unknown'))
		if r.status_code != 200:
			print ('%s ERROR!'%(r.status_code))
			self.testvalue=False
		else:
			print('状态码：%s' %r.status_code)

	def run(self):
		key = self.keys.next()
		self.url = ''.join(['http://',self.ip,self.path+key])
		b64_key = base64.b64encode(key.encode())
		print(self.url)
		data = {
			"Row":[{"key":b64_key.decode(),
			"Cell":[{"column":"c3R1ZGVudDpvcmRlck5v",
			"$":"IjIwMTUwODMwMDA0MzYzIg=="},
			{"column":"c3R1ZGVudDphY3Rpb24=",
			"$":"IjQwMiI="},
			{"column":"c3R1ZGVudDp1aWQ=",
			"$":"IjEyMzQ1Ig=="},
			{"column":"c3R1ZGVudDpkYXRldGltZQ==",
			"$":"IjE0NDA5NTAzODgi"}]}]
		}
		r = self.session.post(self.url,data=json.dumps(data),headers={'content-type':'application/json','accept':'application/json'},timeout=(2,5))
		assert r.status_code == 200,str(r.status_code)+'error'
		
if __name__ == "__main__":
	c = Case3()
	c.run()