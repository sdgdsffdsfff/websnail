import re,logging,os
from math import ceil

logging.basicConfig(
		level = logging.INFO,
		format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
		datefmt = '%Y-%m-%d %H:%M:%S',
		filename = os.path.join(os.getcwd(),'websnail.log'),
		filemode = 'a'
	)

def autofit(concurrent):
	c = concurrent
	if c>0 and c<=100:
		return(1,round(c*1.01))
	elif c>100 and c<=300:
		c = c*1.01
		return(round(c/100),ceil(c/round(c/100)))
	elif c>300 and c<=500:
		c = c*1.02
		return(round(c/100),ceil(c/round(c/100)))
	elif c>500 and c<=800:
		c = c*1.03
		return(round(c/100),ceil(c/round(c/100)))
	elif c>800 and c<=1000:
		c = c*1.06
		return(round(c/100),ceil(c/round(c/100)))
	elif c>1000 and c<=5000:
		c = c*1.1
		return(20,ceil(c/20))
	else:
		return(None,None)

def reviseUrl(url):
	possibles = [
			r"^http://wb-img.u.qiniudn.com/[\w-]{45}(.png|.jpg|.bmp|.gif)$",
			r"^http://wb-img.u.qiniudn.com/[\w-]{45}",
			r"^http://wb-img.u.qiniudn.com/?",
			r"^[\w-]{45}(.png|.jpg|.bmp|.gif)$"
			]
	for index,regx in enumerate(possibles):
		pattern = re.compile(regx)
		match = pattern.match(url)
		#print("index:%s match:%s"%(index,match))
		if match and index == 0:
			return url[-49:]
		if match and index == 1:
			return url[-45:]
		elif match and index == 2:
			return None
		elif match and index == 3:
			return url
		else:
			continue
	return None

def stripformat(data):
	import re,json
	newdata = "{"
	if data:
		pattern = re.compile(r'[^\s]')
		match = pattern.findall(data)
		if match:
			newdatas = ''.join(match).split(',')
			for line in newdatas:
				newdata += "\n"
				newdata += "	"*3
				newdata += line
				newdata += ","
			newdata = newdata[:-1] + "\n		}"
			return newdata
		else:
			return None
	else:
		return None

if __name__ == '__main__':
	s = '"111":"22","33":"44"'
	print(stripformat(s))
	#a,b = autofit(6000)
	#print(a,b)
