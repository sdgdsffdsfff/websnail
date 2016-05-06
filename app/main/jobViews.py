from flask import request,session,render_template,redirect,url_for,flash,jsonify
from json import JSONEncoder
from .snail.run import TestJob
from .Public import autofit,logging
from . import main
from .forms import JobForm
from ..models import db,Script,Testsuit,Job,Report,Service
from flask.ext.login import login_required
from multiprocessing import Manager
import os,time,threading,json,traceback

logpath = os.sep.join([os.getcwd(),'datas','logs'])
statusfile = os.sep.join([os.getcwd(),'datas','jobstatus','TestJob%s'])
reportfile = os.sep.join([os.getcwd(),'datas','reports','report%s'])
scriptpath = os.sep.join([os.getcwd(),'datas','scripts'])
controller = Manager().dict()
## 0:初始化  1：正在运行  2：暂停  -1：停止
controller['status'] = 0

@main.route('/',methods=['POST','GET'])
@main.route('/testjobs',methods=['POST','GET'])
@login_required
def testjobs():
	job = None
	jobs = None
	try:
		job = Job.query.filter_by(status=1).first() or Job.query.filter_by(status=-2).first()
		jobs = Job.query.filter("status!=-1").order_by(Job.id.desc()).all()
	except:
		errorinfo = traceback.format_exc()
		logging.error("数据库异常："+errorinfo)
		flash({"type":"error","message":"数据库异常！"})
		return render_template('dberror.html',errorinfo=errorinfo.split('\n'))
	if job is not None:
		if job.status == 1:
			flash({"type":"info","message":"一个任务正在运行！"})
			return render_template('testjobs.html',showstatus=True,jobs=jobs)
		else:
			return render_template('testjobs.html',showstatus=False,jobs=jobs)
	else:
		controller['status'] = 0
	services = [(service.id,service.name) for service in Service.query.order_by(Service.id.desc()).all()]
	choicesFile = [(script.id,script.filename) for script in Script.query.filter_by(status=0).order_by(Script.id.desc()).all()]
	jobform = JobForm()
	jobform.service.choices = services
	jobform.selectfile.choices = choicesFile

	if request.method == 'POST':
		if jobform.run_time.data is not None and jobform.run_num.data is not None:
			flash({"type":"error","message":"新增失败！并发时间、循环次数 只能选填一个！"})
			return(redirect(url_for('.testjobs')))
		elif jobform.run_time.data is None and jobform.run_num.data is None:
			flash({"type":"error","message":"新增失败！并发时间、循环次数 不能同时为空！"})
			return(redirect(url_for('.testjobs')))		

		testjob = newTestjob(jobform)

		if testjob == 'testerror':
			pass
		elif testjob is None:
			flash({"type":"error","message":"新增失败，数据库异常！"})
		else:
			runjob(testjob)
		return(redirect(url_for('.testjobs')))
	
	return(render_template('testjobs.html',jobs=jobs,jobform=jobform))

def runjob(testjob):
	job = None
	try:
		job = Job.query.filter_by(id=testjob.id).first()
	except:
		logging.error("运行异常："+traceback.format_exc())
		flash({"type":"error","message":"运行异常，查看日志获取详情！"})
		return None
	if job is not None:
		try:
			testjob.start()
			job.status = 1
			db.session.add(job)
			db.session.commit()
		except:
			logging.error("运行异常："+traceback.format_exc())
			flash({"type":"error","message":"运行异常，查看日志获取详情！"})

def newTestjob(form):
	serviceid = None
	scriptid = None
	scriptname = None
	address = None
	process_num,thread_num = autofit(form.concurrent.data)

	for i,v in form.selectfile.choices:
		if i == int(form.selectfile.data):
			scriptid = i
			scriptname = v

	for j,w in form.service.choices:
		if j == int(form.service.data):
			serviceid = j
			address = Service.query.filter_by(id=j).first().address

	'''
	保证测试服务的address的唯一性,通过address进行关联
	'''
	job = Job(serviceid = serviceid,
				scriptid = scriptid,
				concurrent = form.concurrent.data,
				p_num = process_num,
				t_num = thread_num,
				run_time = form.run_time.data,
				run_num = form.run_num.data
				)

	try:
		db.session.add(job)
		db.session.commit()
	except:
		logging.error('数据库提交异常：'+traceback.format_exc())
		db.session.rollback()
		return None

	testJob = TestJob(job.id,
			job.concurrent,
			job.p_num,
			job.t_num,
			job.run_time,
			job.run_num,
			scriptpath,
			scriptname,
			address,
			logpath,
			statusfile %job.id,
			reportfile %job.id,
			controller
			)

	result = testJob.runTest()

	#当status返回为failed时，脚本自测失败
	if result['status'] == 'failed':
		flash({"type":"info","message":result['errorinfo']})
		db.session.delete(job)
		db.session.commit()
		return("testerror")

	return(testJob)

@main.route('/pause/<id>',methods=['POST'])
def pause(id):
	job = Job.query.filter_by(id=id).first()
	if job:
		controller['status'] = 2
		job.status = -2
		db.session.add(job)
		db.session.commit()
		return jsonify(controller)
	else:
		return "no running job"

@main.route('/continue/<id>',methods=['POST'])
def continuing(id):
	job = Job.query.filter_by(id=id).first()
	if job:
		controller["status"] = 1
		job.status = 1
		db.session.add(job)
		db.session.commit()
		return jsonify(controller)
	else:
		return "no ran job"

@main.route('/stopjob/<id>',methods=['POST'])
def stopjob(id):
	job = Job.query.filter_by(id=id).first()
	if job:
		controller['status'] = -1
		while True:
			if controller['status'] == -2:
				break
			time.sleep(0.5)
		db.session.delete(job)
		db.session.commit()
		os.remove(statusfile %job.id)
		flash({"type":"info","message":"任务已停止！"})
		return jsonify(controller)
	else:
		return "no running job"
# ==================================================================================================#
@main.route('/deljob/<id>')
@login_required
def deljob(id):
	info = {"result":True,"errorMsg":None}
	try:
		dbjob = Job.query.filter_by(id=id).first()
		if dbjob:
			if dbjob.status != 1:
				dbjob.status = -1
				db.session.add(dbjob)
				db.session.commit()
			else:
				info = {"result":False,"errorMsg":"任务正在运行,不允许删除"}
	except Exception as e:
		logging.error("数据库异常:%s" %str(e))
		info = {"result":False,"errorMsg":"数据库异常"}
	finally:
		return jsonify(info)

@main.route('/getStatus')
@login_required
def getStatus():
	job = None
	try:
		job = Job.query.filter_by(status=1).first() or Job.query.filter_by(status=-2).first()
	except:
		errorinfo = traceback.format_exc()
		logging.error("数据库异常！"+errorinfo)
		progress = JSONEncoder().encode({"status":-1,"errorinfo":"数据库异常！"})
		return(progress)

	if job is not None:
		if job.status == -2:
			return "pause"
		try:
			with open(statusfile %job.id,'r') as f:
				status = json.load(f)
				progress = status
				if status['status'] == 1:  #status中的status值为1时表示已完成
					job.status = 2   #将job的状态置为已完成(2)
					with open(reportfile %job.id,'r') as f:
						result = json.load(f)
					report = Report(
							jobid = job.id,
							logpath = result['logpath'],
							totalrequests = result['totalrequests'],
							averagetime = result['averagetime'],
							throught = result['throught'],
							min_span = result['min_span'],
							max_span = result['max_span'],
							errorcount = result['errorcount'],
							errorcounter = result['errorcounter'],
							customtimers = result['customtimers'],
							customscore = result['customscore']
							)
					db.session.add(job)
					db.session.add(report)
					db.session.commit()
					os.remove(statusfile %job.id)
					os.remove(reportfile %job.id)
		except ValueError:
			progress = {'average':'正在获取..', 'throught':'正在获取..','threads': '正在获取..', 'errors': '正在获取..', 'status': 0, 'progress':'正在获取..', 'TotalRequest':'正在获取..'}
		except OSError:
			progress = {"status":-1,"errorinfo":traceback.format_exc()}
		except:
			logging.error("执行异常:"+traceback.format_exc())
			job.status = 0
			db.session.add(job)
			db.session.commit()
			progress = {"status":-1,"errorinfo":"脚本运行异常,查看错误日志获取详情！"}
		finally:
			return(JSONEncoder().encode(progress))
	else:
		return("none")
