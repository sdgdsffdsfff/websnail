from datetime import datetime
from flask.ext.login import UserMixin
from . import db,login_manager

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model,UserMixin):
	id = db.Column(db.Integer,primary_key=True)
	email = db.Column(db.String(64),unique=True,index=True)
	username = db.Column(db.String(64),unique=True,index=True)
	password = db.Column(db.String(128))
	createdtime = db.Column(db.DateTime,default=datetime.now)

class Script(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	filename = db.Column(db.String(30))
	desc = db.Column(db.String(100))
	path = db.Column(db.String(100))
	content = db.Column(db.PickleType)
	status = db.Column(db.Integer,default=0)
	lastedittime = db.Column(db.DateTime,default=datetime.now)
	createdtime = db.Column(db.DateTime,default=datetime.now)
	
	def __init__(self,filename,desc,path,content,status=0):
		self.filename = filename
		self.desc = desc
		self.path = path
		self.content = content
		self.status = status

class Testsuit(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(30))
	servicetype = db.Column(db.String(20))
	size = db.Column(db.Integer,default=0)
	suitfile = db.Column(db.String(100))
	status = db.Column(db.Integer,default=0)
	createdtime = db.Column(db.DateTime,default=datetime.now)

class Job(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	address = db.Column(db.String(30))
	servicetype = db.Column(db.String(20))
	serviceversion = db.Column(db.String(20))
	filename = db.Column(db.String(100))
	concurrent = db.Column(db.Integer,default=0)
	p_num = db.Column(db.Integer,default=0)
	t_num = db.Column(db.Integer,default=0)
	run_time = db.Column(db.Integer,default=0)
	run_num = db.Column(db.Integer,default=0)
	relatesuitid = db.Column(db.Integer)
	relatesuitname = db.Column(db.String(30))
	status = db.Column(db.Integer,default=1)
	createdtime = db.Column(db.DateTime,default=datetime.now)
	
	def __init__(self,address,servicetype,serviceversion,filename,relatesuitid,relatesuitname,concurrent=0,p_num=0,t_num=0,run_time=0,run_num=0):
		self.address = address
		self.filename = filename
		self.servicetype = servicetype
		self.serviceversion = serviceversion
		self.relatesuitid = relatesuitid
		self.relatesuitname = relatesuitname
		self.concurrent = concurrent
		self.p_num = p_num
		self.t_num = t_num
		self.run_time = run_time
		self.run_num = run_num
	
	def __repr__(self):
		return('TestJob:{id}'.format(id=self.id))

class Report(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	jobid = db.Column(db.Integer)
	servicetype = db.Column(db.String(20))
	logpath = db.Column(db.String(100))
	totalrequests = db.Column(db.Integer)
	averagetime = db.Column(db.Float)
	throught = db.Column(db.Float)
	min_span = db.Column(db.Float)
	max_span = db.Column(db.Float)
	errorcount = db.Column(db.Integer)
	errorcounter = db.Column(db.PickleType)
	customtimers = db.Column(db.PickleType)
	customscore = db.Column(db.PickleType)
	createdtime = db.Column(db.DateTime,default=datetime.now)

	def __init__(self,jobid,servicetype,logpath,totalrequests,averagetime,throught,
				min_span,max_span,errorcount,
				errorcounter,customtimers,customscore):
		self.jobid = jobid
		self.servicetype = servicetype
		self.logpath = logpath
		self.totalrequests = totalrequests
		self.averagetime = averagetime
		self.throught = throught
		self.min_span = min_span
		self.max_span = max_span
		self.errorcount = errorcount
		self.errorcounter = errorcounter
		self.customtimers = customtimers
		self.customscore = customscore
	
	def __repr__(self):
		return('TestResult:{id}'.format(id=self.id))

class Downimg(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	filename = db.Column(db.String(100))
	directory = db.Column(db.String(100))    #csv文件存放路径
	concurrent = db.Column(db.Integer,default=0)
	total_count = db.Column(db.Integer,default=0)
	downlogdir = db.Column(db.String(100)) #下载结果log存放路径
	status = db.Column(db.Integer,default=0)
	createdtime = db.Column(db.DateTime,default=datetime.now)
	endtime = db.Column(db.DateTime)

	def __init__(self,filename,directory,concurrent,total_count,downlogdir):
		self.filename = filename
		self.directory = directory
		self.concurrent = concurrent
		self.total_count = total_count
		self.downlogdir = downlogdir
	
	def __repr__(self):
		return("DownImg:{id}".format(id=self.id))

class Service(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(50))
	address = db.Column(db.String(50),unique=True)
	typename = db.Column(db.String(20))
	status = db.Column(db.Integer,default=0)
	createdtime = db.Column(db.DateTime,default=datetime.now)

class Servicetype(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	typename = db.Column(db.String(10))


if __name__ == "__main__":
	job = Job('1234',10,20,30)
	report = Report('this is a test',1)
	script = Script('test.py','123','1234','2346',0)
	print('ok')
