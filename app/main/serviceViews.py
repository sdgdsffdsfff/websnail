from flask import request,session,render_template,redirect,url_for,flash
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
		servicetypes = [(i+1,v.typename) for i,v in enumerate(Servicetype.query.order_by('id').all())]
	except:
		errorinfo = traceback.format_exc()
		logging.error("数据库异常："+errorinfo)
		flash({"type":"error","message":"数据库异常！"})
		return render_template('dberror.html',errorinfo=errorinfo.split('\n'))

	form = ServiceForm()
	form.type.choices = servicetypes
	
	if request.method == "POST" and form.validate_on_submit():
		if saveService(form) is None:
			flash({"type":"error","message":"新增失败：请不要添加重复的服务！"})
		
		return redirect(url_for('.services'))
	
	return(render_template('services.html',form=form,services=services))

def saveService(form):
	for i,v in form.type.choices:
		if i == int(form.type.data):
			typename = v

	service = Service(
			name = form.name.data,
			address = form.address.data,
			typename = typename
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
	try:
		service = Service.query.filter_by(id=id).first()
		if service is not None:
			db.session.delete(service)
			db.session.commit()
			flash({"id":id,"type":"info","message":"删除成功！您刚刚删除了一个服务：{name}--{address}".format(name=service.name,address=service.address)})
			return("success")
		else:
			flash({"type":"error","message":"删除失败！该条记录不存在！"})
			return("failed")
	except:
		logging.error("数据库异常："+traceback.format_exc())
		flash({"type":"error","info":"数据库异常！删除失败！"})
		return("failed")

