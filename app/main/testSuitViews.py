from flask import request,session,render_template,redirect,url_for,flash
from werkzeug import secure_filename
from .Public import autofit,reviseUrl,logging
from flask.ext.login import login_required
from . import main
from .forms import TestSuitForm
from datetime import datetime
from ..models import db,Testsuit,Servicetype
import json,os,pandas as pd,traceback

imgdir = '/data/websnail/resources/imgs'
sourcefiledir = os.path.join(os.getcwd(),'datas','suitfiles','sourcefile')
suitfiledir = os.path.join(os.getcwd(),'datas','suitfiles','suitdata')

#############################################################以下是testsuits的视图##########################################################
@login_required
@main.route('/testsuits',methods=["GET","POST"])
def testSuits():
	testSuits = None
	servicetypes = []
	try:
		testSuits = Testsuit.query.filter_by(status=0).order_by(Testsuit.id.desc()).all()
		servicetypes = [(i+1,v.typename) for i,v in enumerate(Servicetype.query.all())]
	except:
		errorinfo = traceback.format_exc()
		logging.error("数据库异常："+errorinfo)
		flash({"type":"error","message":"数据库异常！"})
		return render_template("dberror.html",errorinfo=errorifo.split('\n'))
		
	suitForm = TestSuitForm()
	suitForm.servicetype.choices = servicetypes

	if request.method == "POST" and suitForm.validate_on_submit():
		suits = []
		suitfile = ''
		for i,v in suitForm.servicetype.choices:
			if i == int(suitForm.servicetype.data):
				try:
					choicedtype = Servicetype.query.all()[i-1] #得到servicetype的数据库对象
				except:
					logging.error("数据库异常："+traceback.format_exc())
					flash({"type":"error","message":"数据库异常！"})
					return(redirect(url_for('.testSuits')))

		suitfile = ''.join([suitfiledir,os.sep,datetime.now().strftime('%Y_%m_%d-%H_%M_%S'),'.',choicedtype.typename.lower()])
		##如果是ocr则允许上传测试集文件，nlp、search等服务逻辑此处留空
		if choicedtype.typename.lower() in ["ocr","getsubject"]:
			if suitForm.filename.data.filename != '':
				file = suitForm.filename.data
				filename = secure_filename(file.filename)
				#if filename[-3:] not in ['csv','txt','xls']:
				#	flash({"type":"error","message":"新增失败！文件格式不支持！"})
				#	return(redirect(url_for('.testSuits')))
				path = os.path.join(sourcefiledir,filename)
				try:
					file.save(path)
					if choicedtype.typename.lower() == 'ocr':
						suitcases = pd.read_csv(path)
						for imgs in suitcases.values:
							imgurl = reviseUrl(imgs[0])
							if imgurl is not None:
								absimg = os.path.join(imgdir,imgurl)
								suits.append(absimg)
					else: #== getsubject
						import pickle
						suits = pickle.load(open(path,'rb'))
				except:
					logging.error("读写文件失败："+traceback.format_exc())
					flash({"type":"error","message":"新增失败！检查错误日志查看详情！"})
					return(redirect(url_for('.testSuits')))
			else:
				flash({"type":"error","message":"新增失败：未上传文件！"})
				return(redirect(url_for('.testSuits')))
		elif choicedtype.typename.lower() in ["nlp","search"]:
			if suitForm.datafile.data != '':
				datafile = suitForm.datafile.data
				if os.path.isfile(datafile):
					try:
						with open(datafile,'r') as f:
							suits = [i.strip() for i in f.readlines() if len(i) > 1]
					except:
						logging.error("文件读取异常："+traceback.format_exc())
						flash({"type":"error","message":"新增失败！文件读取异常！"})
						return(redirect(url_for('.testSuits')))

					if len(suits) == 0:
						flash({"type":"error","message":"新增失败：指定数据文件内容为空！"})
						return(redirect(url_for('.testSuits')))
				else:
					flash({"type":"error","message":"新增失败，文件不存在！"})
					return(redirect(url_for('.testSuits')))

			else:
				flash({"type":"error","message":"新增失败：数据文件路径不允许空值！"})
				return(redirect(url_for('.testSuits')))
		elif choicedtype.typename.lower() in ['1v1','none']:
			suits = []
		else:
			flash({"type":"error","message":"新增失败：没有指定的服务类型！"})
			return(redirect(url_for('.testSuits')))
		
		try:
			json.dump(suits,open(suitfile,'w'))
		except:
			logging.error("序列化失败："+traceback.format_exc())
			flash({"type":"error","message":"新增失败！检查错误日志查看详情！"})
			return(redirect(url_for('.testSuits')))

		testsuit = Testsuit(
				name = suitForm.name.data,
				servicetype = choicedtype.typename,
				size = len(suits),
				suitfile = suitfile
			)
		try:
			db.session.add(testsuit)
			db.session.commit()
		except:
			logging.error("数据库提交异常："+traceback.format_exc())
			flash({"type":"error","message":"新增失败！数据库异常！"})
			return(redirect(url_for('.testSuits')))
		flash({"type":"info","message":"新增成功！您刚刚新增了一个测试集!"})
		return(redirect(url_for('.testSuits')))

	return(render_template('testsuits.html',testSuits=testSuits,form=suitForm))


@login_required
@main.route('/delsuit/<id>')
def delSuit(id):
	suit = None
	try:
		suit = Testsuit.query.filter_by(id=id).first()
		if suit is not None:
			suit.status = -1
			db.session.add(suit)
			db.session.commit()
			flash({"id":id,"type":"del","message":"删除成功！您刚刚删除了一个测试集！"})
			return("success")
		else:
			flash({"type":"error","message":"删除失败！未找到指定的测试集，或已被删除！"})
			return("failed")
	except:
		logging.error("数据库异常："+traceback.format_exc())
		flash({"type":"error","message":"删除失败！数据库异常！"})
		return("failed")

