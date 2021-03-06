#encoding:utf-8
from flask import request,session,render_template,redirect,url_for,flash,jsonify
from datetime import datetime
from . import main
from .forms import ScriptForm,TSForm
from ..models import db,Script,Service
from .Public import logging
import os,traceback,time
from json import JSONEncoder
from flask.ext.login import login_required

scriptpath = os.sep.join([os.getcwd(),'datas','scripts'])

#############################################################以下是script的视图##########################################################
@main.route('/scripts',methods=['POST','GET'])
@login_required
def scripts():
	scripts = None
	form = TSForm()
	form.service.choices = [(i+1,service.name) for i,service in enumerate(Service.query.filter_by(status=0).all())]

	try:
		scripts = Script.query.filter("status != -1").order_by(Script.id.desc()).all()
	except:
		errorinfo = traceback.format_exc()
		logging.error("数据库异常:"+errorinfo)
		flash({"type":"error","message":"数据库异常！"})
		return render_template('dberror.html',errorinfo=errorinfo.split('\n'))
	
	if request.method == 'POST' and form.validate_on_submit():
		service = None
		scriptForm = ScriptForm()

		for i,v in form.service.choices:
			if i == int(form.service.data):
				service = Service.query.filter_by(id=i).first()

		base_content = ''
		with open(os.path.join(scriptpath,'script.base'),'r') as f:
			base_content = f.read().strip()

		headers = None
		counter = ""
		if form.need_headers.data:
			headers = form.headers.data
		else:
			headers = {}
		
		if form.returnfield.data:
			fields = form.returnfield.data.split(',')
			for field in fields:
				counter += "self.custom_timers['{field}']=r.json()['{field}']".format(field=field)
				counter += "\n"
				counter += "	"*2
		
		data = stripformat(form.data.data[1:-1]) if form.data.data and form.data.data.startswith('{') and form.data.data.endswith('}') else stripformat(form.data.data)

		content = base_content.format(
			url=service.address,
			headers=headers,
			conn_timeout=form.connect_timeout.data or 30,
			resp_timeout=form.response_timeout.data or 60,
			method=service.method.lower(),
			param_type="data" if service.method.lower() == "post" else "params",
			data=data,
			counter=counter
			)

		service_scripts = Script.query.filter_by(serviceid=service.id).all()

		scriptForm.scriptname.data = "Case_%s_%s.py" %(service.name,len(service_scripts)+1)
		scriptForm.desc.data = "测试脚本"
		scriptForm.content.data = content
		saveEdit(scriptForm,serviceid=service.id)
		scriptid = Script.query.order_by(Script.id.desc()).first().id

		return redirect(url_for('.editScript',id=str(scriptid)))
	
	return(render_template('scripts.html',scripts=scripts,form=form))

def stripformat(data):
	import re
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

@main.route('/editscript/<id>',methods=['POST','GET'])
@login_required
def editScript(id):
	script = getDiffScript(id)
	scriptForm = ScriptForm()

	if script is None:
		flash({"type":"error","message":"编辑失败！未找到对应脚本！"})
		return(redirect(url_for('.scripts')))
	if request.method == 'POST' and scriptForm.validate():
		if scriptForm.content.data != '':
			saveEdit(scriptForm,script=script)
			return(redirect(url_for('.scripts')))
		else:
			flash({"type":"error","message":"编辑失败，脚本内容不允许空！"})
			return(redirect(url_for('.scripts')))

	scriptForm.scriptname.data = script.filename	
	scriptForm.desc.data = script.desc
	scriptForm.content.data = script.content

	return render_template('editscript.html',form=scriptForm,id=id)

@main.route('/delscript/<int:id>')
@login_required
def delScript(id):
	info = {"result":True,"errorMsg":None}
	try:
		script_del = Script.query.filter_by(id=id).first()
		if script_del:
			script_del.status = -1
			db.session.add(script_del)
			db.session.commit()
		else:
			info = {"result":False,"errorMsg":"脚本不存在或已被删除"}
	except:
		logging.error("数据库异常："+traceback.format_exc())
		info = {"result":False,"errorMsg":"数据库异常"}
	finally:
		return jsonify(info)

@main.route("/tests",methods=["POST"])
@login_required
def tests():
	import subprocess
	code = request.form.get("code")
	tempfile = os.sep.join([scriptpath,"tmp.py"])
	with open(tempfile,'w+') as f:
		f.write(code)
	info = subprocess.Popen(
				'python %s' %tempfile,
				stderr=subprocess.PIPE,
				stdout=subprocess.PIPE,
				shell=True
			)
	testResult = {}
	infos = info.stderr.readlines()
	if infos:
		testResult["type"] = "error"
		testResult["info"] = "\r\n".join([i.decode() for i in infos])
	else:
		testResult["type"] = "pass"
		testResult["info"] = "\r\n".join([i.decode() for i in info.stdout.readlines()])
	
	return JSONEncoder().encode(testResult)

		
@main.route('/testscript/<int:id>')
@login_required
def testScript(id):
	import subprocess
	script = None
	form = ScriptForm()
	try:
		script = getDiffScript(id)
	except:
		logging.error("脚本对比异常："+traceback.format_exc())
		testResult["type"] = "error"
		testResult["info"] = traceback.format_exc()
		return JSONEncoder().encode(testResult)
	testResult = {}
	if script is not None:
		filename = os.sep.join([script.path,script.filename])	
		info = subprocess.Popen(
					'python %s' %filename,
					stderr=subprocess.PIPE,
					stdout=subprocess.PIPE,
					shell=True
				)
		infos = info.stderr.readlines()
		if infos:
			testResult["type"] = "error"
			testResult["info"] = "\r\n".join([i.decode() for i in infos])
		else:
			testResult["type"] = "pass"
			testResult["info"] = "\r\n".join([i.decode() for i in info.stdout.readlines()])
			
		return JSONEncoder().encode(testResult)
	else:
		testResult["type"] = "error"
		testResult["info"] = "未知异常，请查看日志获取详细信息！"
		return JSONEncoder().encode(testResult)

def getDiffScript(id):
	script = Script.query.filter_by(id=id).first()
	filepath = script.path
	if os.path.isdir(filepath):
		filename = os.sep.join([filepath,script.filename])	
		if os.path.isfile(filename): #如果本地脚本存在，则对比脚本文件和数据库记录是否一致
			with open(filename,'r') as f:
				fileContent = f.read()
			if script.content != fileContent:
				script.content = fileContent   #如果脚本内容和数据库内容不一致，以脚本内容为准,并更新该条记录
				db.session.add(script)
				db.session.commit()
			return(script)
		else: #如果本地脚本文件被删除，则初始化创建脚本
			with open(filename,'w') as f:
				f.write(script.content)
			return(script)
	else:
		return(None)

def saveEdit(scriptForm,serviceid=None,script=None):
	mode = 0 #编辑
	if script is None:
		mode = 1 #新增
		script = Script(
			filename = scriptForm.scriptname.data,
			desc = scriptForm.desc.data,
			path = scriptpath,
			content = scriptForm.content.data,
			serviceid=serviceid
		)
	else:
		script.filename = scriptForm.scriptname.data
		script.desc = scriptForm.desc.data
		script.content = scriptForm.content.data
		script.lastedittime = datetime.now()

	saveok = saveScriptFile(script)
	if saveok:
		try:
			db.session.add(script)
			db.session.commit()
		except:
			logging.error("数据库异常："+traceback.format_exc())
	else:
		flash({"type":"error","message":"保存脚本失败！查看错误日志获取详细信息！"})
		return

	if mode == 1:
		flash({"type":"info","message":"您刚刚新增了一个脚本：{name}".format(name=script.filename)})
	
def saveScriptFile(script):
	if os.path.isdir(script.path):
		try:
			with open(os.sep.join([script.path,script.filename]),'w') as f:
				f.write(script.content)
		except:
			logging.error("写磁盘文件异常："+traceback.format_exc())
			flash({"type":"error","message":"未知异常，脚本内容过大或磁盘空间已满"})
			return(False)
		return(True)
	else:
		return(False)
