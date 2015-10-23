from flask import redirect,flash,url_for
from . import main
from ..models import db,Script,Testsuit,Job,Service,Report
from .Public import logging
import traceback

@main.route('/resume<type>/<id>')
def resumeJob(type,id):
	underResumes = []
	url_map = {
		"job":".testjobs",
		"script":".scripts",
		"service":".services",
		"suit":".testSuits"
	}
	if type == 'job':
		job = None
		report = None
		try:
			job = Job.query.filter_by(id=id).first()
			report = Report.query.filter_by(jobid=id).first()
		except:
			logging.error("数据库异常：" + traceback.format_exc())
			flash({"type":"error","message":"恢复失败！数据库异常！"})
			return(redirect(url_for(url_map[type])))

		if report is not None:
			job.status = 2
		else:
			job.status = 0
		underResumes.append(job)
	elif type == 'script':
		script = Script.query.filter_by(id=id).first()
		if script is not None:
			script.status = 0
		underResumes.append(script)
	elif type == 'service':
		service = Service.query.filter_by(id=id).first()
		if service is not None:
			service.status = 0
		underResumes.append(service)
	elif type == 'suit':
		suit = Testsuit.query.filter_by(id=id).first()
		if suit is not None:
			suit.status = 0
		underResumes.append(suit)

	for thing in underResumes:
		if thing is not None:
			try:
				db.session.add(thing)
				db.session.commit()
			except:
				logging.error("数据库提交异常："+traceback.format_exc())
				flash({"type":"error","message":"数据库提交异常！"})
				return(redirect(url_for(url_map[type])))

	flash({"id":id,"type":"info","message":"恢复成功！"})
	logging.info("恢复记录{type}，ID:{id}".format(type=type,id=id))
	return(redirect(url_for(url_map[type])))
