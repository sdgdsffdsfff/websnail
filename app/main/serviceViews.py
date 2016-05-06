from flask import request,session,render_template,redirect,url_for,flash,jsonify
from . import main
from .forms import ServiceForm
from ..models import db,Service,Servicetype
from .Public import logging
from flask.ext.login import login_required
import traceback

#############################################################以下是service的视图##########################################################
@main.route('/services',methods=['GET','POST'])
@login_required
def services():
	services = None
	servicetypes = []
	try:
		services = Service.query.order_by(Service.id.desc()).all()
	except:
		errorinfo = traceback.format_exc()
		logging.error("数据库异常："+errorinfo)
		flash({"type":"error","message":"数据库异常！"})
		return render_template('dberror.html',errorinfo=errorinfo.split('\n'))

	form = ServiceForm()
	form.methodtype.choices = [(i+1,v) for i,v in enumerate(['GET','POST'])]

	if request.method == "POST" and form.validate_on_submit():
		if saveService(form) is None:
			flash({"type":"error","message":"新增失败：请不要添加重复的服务！"})
		
		return redirect(url_for('.services'))
	
	return(render_template('services.html',form=form,services=services))

def saveService(form):
	method = None
	for i,v in form.methodtype.choices:
		if i == int(form.methodtype.data):
			method = v

	service = Service(
			name = form.name.data,
			address = form.address.data,
			method = method
		)

	try:
		db.session.add(service)
		db.session.commit()
	except:
		logging.error("数据库提交异常："+traceback.format_exc())
		return None
	flash({"type":"info","message":"新增成功！"})
	return(service)

@main.route('/delservice/<id>')
@login_required
def delService(id):
	info = {"result":True,"errorMsg":None}
	try:
		service = Service.query.filter_by(id=id).first()
		if service is not None:
			db.session.delete(service)
			db.session.commit()
		else:
			info = {"result":False,"errorMsg":"该条记录不存在或已被删除"}
	except:
		logging.error("数据库异常："+traceback.format_exc())
		info = {"result":False,"errorMsg":"数据库异常！删除失败！"}
	finally:
		return jsonify(info)

