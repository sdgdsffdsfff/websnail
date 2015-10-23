from flask import request,session,render_template,flash,redirect,url_for
from datetime import datetime
from json import JSONEncoder
from werkzeug.utils import secure_filename
from .downfile.downimg import DownImgJob
from . import main
from .Public import autofit,logging
from .forms import FileForm
from ..models import db,Downimg
import re,os,threading,queue,pandas as pd,traceback
from flask.ext.login import login_required

logpath = '/data/websnail/downimglogs'
imgdir = '/data/websnail/resources/imgs'

######################################下面是下载图片页面####################################
@main.route('/downimgs',methods=['GET','POST'])
@login_required
def downImgs():
	fileform = FileForm()
	if request.method == 'POST' and fileform.validate():
		file = fileform.filename.data
		filename = secure_filename(file.filename)
		if filename[-3:] not in ['csv','txt','xls','xlsx']:
			flash({"type":"error","message":"文件格式不正确！请选择以下格式文件:csv、txt、xls、xlsx"})
			return(redirect(url_for('.downImgs')))

		directory = fileform.directory.data
		if os.path.isdir(directory):
			savepath = os.path.join(directory,filename)
			try:
				file.save(savepath)
			except:
				logging.error("文件存储失败："+traceback.format_exc())
				flash({"type":"error","message":"文件存储失败！检查目录读写权限及磁盘空间！"})
				return(redirect(url_for('.downImgs')))
		else:
			flash({"type":"error","message":"路径不存在！请重新填写"})
			return(redirect(url_for('.downImgs')))
			
		concurrent = fileform.concurrent.data
		que = queue.Queue()
		#日志存放路径
		downlogdir = os.path.join(logpath,'downloadjob',datetime.now().strftime('%Y_%m_%d-%H_%M_%S'))
		if not os.path.isdir(downlogdir):
			try:
				os.makedirs(downlogdir)
			except:
				logging.error("创建下载目录失败："+traceback.format_exc())
				flash({"type":"error","message":"创建下载目录失败！检查目录读写权限及磁盘空间！"})
				return(redirect(url_for('.downImgs')))
		#生成任务队列
		datas = None
		try:
			datas = [value[0] for value in pd.read_csv(savepath).values]
		except:
			logging.error("上传文件格式或内容异常！"+traceback.format_exc())
			flash({"type":"error","message":"上传文件格式或内容异常！"})
			return(redirect(url_for('.downImgs')))

		for url in datas:
			revisedurl = reviseUrl(url)
			if revisedurl is not None:
				que.put("http://wb-img.u.qiniudn.com/"+revisedurl)
			else:
				logname = os.path.join(downlogdir,'failed')
				try:
					with open(logname,'a') as f:
						f.write(url+'\n')
				except:
					logging.error("写磁盘空间异常！"+traceback.format_exc())
					flash({"type":"error","message":"写磁盘空间异常！"})
					return(redirect(url_for('.downImgs')))
					
		#数据库中生成下载任务历史记录
		downimg = Downimg(
				filename = filename,
				directory = directory,
				concurrent = concurrent,
				total_count = que.qsize(),
				downlogdir = downlogdir
			)

		try:
			db.session.add(downimg)
			db.session.commit()
		except:
			logging.error("数据库提交异常："+traceback.format_exc())
			flash({"type":"error","message":"数据库异常！"})

		t = threading.Thread(target=downloadimg,args=(que,concurrent,downimg.id,downlogdir,))
		t.setDaemon(True)
		t.start()

		flash({"id":downimg.id,"type":"download","message":"图片已在后台下载！"})
		
	return(render_template('downimgs.html',fileform=fileform))

def downloadimg(que,concurrent,jobid,downlogdir):
	p_num,t_num = autofit(concurrent)

	downjob = DownImgJob(
				que,
				imgdir,
				p_num,
				t_num,
				downlogdir
			)
	
	downjob.run()
	
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
		if match and index == 0:
			return url[-49:]
		elif match and index == 1:
			return url[-45:]
		elif match and index == 2:
			return None
		elif match and index == 3:
			return url
		else:
			continue
	return None

@main.route('/getdownloadstatus/<id>')
@login_required
def getDownloadStatus(id):
	job = Downimg.query.filter_by(id=id).first()

	if job is not None:
		downstatus = {"failed":[],
					"exists":[],
					"status":"未完成",
					"total_count":job.total_count,
					"failed_count":0,
					"exists_count":0
					}

		if os.path.isfile(os.path.join(job.downlogdir,'done')):
			job.status = 1
			job.endtime = datetime.now()

			try:
				db.session.add(job)
				db.session.commit()
			except:
				logging.error('数据库提交异常：'+traceback.format_exc())
				return -1

			downstatus['status'] = "已完成" 
		try:
			if os.path.isfile(os.path.join(job.downlogdir,'failed')):
				downstatus = readStatus(job,downstatus,'failed')

			if os.path.isfile(os.path.join(job.downlogdir,'exists')):
				downstatus = readStatus(job,downstatus,'exists')

			return JSONEncoder().encode(downstatus)
		except:
			logging.error("读取文件异常："+traceback.format_exc())
			return -1
	else:
		return -1

def readStatus(job,downstatus,type):
	with open(os.path.join(job.downlogdir,type)) as f:
		typelist = [i.strip() for i in f.readlines() if len(i)>1]
		downstatus[type] = list(set(typelist))
		downstatus['{type}_count'.format(type=type)] = len(typelist)
	return downstatus

if __name__ == '__main__':
	url = "http://wb-img.u.qiniudn.com/"
	#url = "http://wb-img.u.qiniudn.com/20150426-7c097ab4-155d-4e32-baa8-abbb7a71b567.png"
	#url = "20150426-B0407B5E-98E2-4385-970A-30F4787F5F63.jpg"
	print(reviseUrl(url))
