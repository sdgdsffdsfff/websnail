from flask import request,render_template,redirect,url_for,flash
from ..models import Report,Job,Servicetype,Testsuit,db
from .forms import AnalysisForm
from .Public import logging
from . import main
from collections import OrderedDict
from json import JSONEncoder
import traceback

@main.route('/analysis',methods=['GET','POST'])
def analysis():
	#取对应job未被删除的最近5个报告对象list
	jobs = None
	reorts = None
	form = None
	r_args = request.args
	if r_args:
		try:
			jobs = Job.query.filter(db.and_(Job.servicetype==r_args.get('type'),Job.status==2,Job.concurrent==r_args.get('conc'),Job.relatesuitname==r_args.get('suit'))).all()[-5:]
			reports = [Report.query.filter_by(jobid=job.id).first() for job in jobs]
		except:
			errorinfo = traceback.format_exc()
			logging.error("数据库异常："+errorinfo)
			flash({"type":"error","message":"数据库异常！"})
			return render_template('dberror.html',errorinfo=errorinfo.split('\n'))
	else:		
		type = 'ocr'
		reports = []
		jobs = []
		servicetypes = []
		concurrents = []
		suits = []
		versions = []

		try:
			reports = [report for report in Report.query.filter_by(servicetype=type).order_by(Report.id.desc()).limit(5).all() if Job.query.filter_by(id=report.jobid).filter_by(status=2).first() is not None][::-1]
			jobs = [Job.query.filter_by(id=report.jobid).first() for report in reports]
			servicetypes = [(i+1,v.typename) for i,v in enumerate(Servicetype.query.all())]
			concurrents = [(j+1,k.concurrent) for j,k in enumerate(Job.query.filter_by(status=2).group_by(Job.concurrent).all())]
			suits = [(l+1,m.name) for l,m in enumerate(Testsuit.query.filter_by(status=0).all())]
		except:
			errorinfo = traceback.format_exc()
			logging.error("数据库异常："+errorinfo)
			flash({"type":"error","message":"数据库异常！"})
			return render_template('dberror.html',errorinfo=errorinfo.split('\n'))

		if not r_args:
			form = AnalysisForm()
			form.servicetype.choices = servicetypes
			form.concurrent.choices = concurrents
			form.suit.choices = suits
			form.serviceversion.choices = versions
	
	if request.method == 'POST':
		for i,j in form.servicetype.choices:
			if i == int(form.servicetype.data):
				servicetype = j
				serviceindex = i-1
		for k,l in form.concurrent.choices:
			if k == int(form.concurrent.data):
				concurrent = l
				concurrentindex = k-1
		for m,n in form.suit.choices:
			if m == int(form.suit.data):
				suit = n
				suitindex = m-1

		try:
			if not form.serviceversion.data:
				jobs = Job.query.filter(db.and_(Job.servicetype==servicetype,Job.status==2,Job.concurrent==concurrent,Job.relatesuitname==suit)).all()[-5:]
				#jobs = Job.query.filter_by(servicetype=servicetype).filter_by(status=2).filter_by(concurrent=concurrent).filter_by(relatesuitname=suit).all()[-5:]
			else:
				datas = {'type':serviceindex,'conc':concurrentindex,'suit':suitindex,'selects':form.serviceversion.data}
				jobs = getVersion(datas)
			reports = [Report.query.filter_by(jobid=job.id).first() for job in jobs]
		except:
			errorinfo = traceback.format_exc()
			logging.error("数据库异常："+errorinfo)
			return redirect(url_for('.analysis'))
	
	tableData = getTableData(jobs,reports)
	linechartData = getLineChartData(jobs,reports)
	barchartData = getBarChartData(jobs,reports)

	return render_template("analysis.html",jobs=jobs,linechartData=linechartData,form=form,tableData=tableData,barchartData=barchartData)

def getTableData(jobs,reports):
	if len(jobs) == 0 or len(reports) == 0:
		return None

	tableData = OrderedDict()

	for i,v in enumerate(reports):
		try:
			suit = Testsuit.query.filter_by(id=jobs[i].relatesuitid).first()
			tableData[i] = [jobs[i].serviceversion,jobs[i].concurrent,suit.name,suit.size,v.averagetime,v.throught,v.customtimers]
		except:
			errorinfo = traceback.format_exc()
			logging.error("数据库异常："+errorinfo)
			return None
	
	return tableData

def getLineChartData(jobs,reports):
	if len(jobs) == 0 or len(reports) == 0:
		return None

	data = {
		'平均响应时间(s)':[report.averagetime for report in reports]
		#'最大响应时间(s)':[report.max_span for report in reports],
		#'最小响应时间(s)':[report.min_span for report in reports]
	}

	xAxisData = [job.serviceversion for job in jobs]
	
	linechartData = {
		"data" : list(data.keys()),
		"xAxisData" : xAxisData,
		"series" : [
			{
				'name':i,
				"type":"line",
				"data":v,
				'markLine':{
					'data':[
						{'type':'average','name':i}
					]
				}
			} for i,v in data.items()]
	}
	
	return linechartData

def getBarChartData(jobs,reports):
	import itertools
	if len(jobs) == 0 or len(reports) == 0:
		return None

	barchartData = OrderedDict()
	dealCustomDict = {}
	multicolors = itertools.cycle(['#EE30A7','#DAA520','#CDCD00','#B22222','#7CFC00','#7A7A7A','#7B68EE','#A0522D','#FFD700','#FFBBFF','#7D26CD','#7CCD7C','#698B22','#87CEFF'])
	singlecolors = itertools.cycle(['red','#00FA9A','green','blue','purple','black'])
	
	for report in reports:
		for key in report.customtimers.keys():
			if key not in dealCustomDict.keys():
				dealCustomDict[key] = {}
			for childkey,value in report.customtimers[key].items():
				if childkey not in dealCustomDict[key].keys():
					dealCustomDict[key][childkey] = []

	for report in reports:
		for k in dealCustomDict.keys():
			if k not in report.customtimers.keys():
				for kk in dealCustomDict[k].keys():
					dealCustomDict[k][kk].append(0)
					
		for key,value in report.customtimers.items():
			for ckey in dealCustomDict[key].keys():
				if ckey not in value.keys():
					dealCustomDict[key][ckey].append(0)
				else:
					dealCustomDict[key][ckey].append(value[ckey])
	
	dealCustomDict['errors'] = {}

	for report in reports:
		if len(report.errorcounter.keys()) == 0:
			dealCustomDict['errors']['0'] = []
		else:
			for ekey in report.errorcounter.keys():
				if ekey not in dealCustomDict['errors'].keys():
					dealCustomDict['errors'][ekey] = []


	for report in reports:
		for m in dealCustomDict['errors'].keys():
			if m not in report.errorcounter.keys():
				dealCustomDict['errors'][m].append(0)
			else:
				dealCustomDict['errors'][m].append(report.errorcounter[m])
	

	series = []
	customs = []

	for parent,child in dealCustomDict.items():
		if len(child) > 1:
			for item,value in child.items():
				serieschild = {
					"type":"bar",
					"tooltip":{
						"trigger":"item",
						"formatter":"{a}<br/>出现个数:{c}"
					},
					"itemStyle":{
						"normal" : {
							"color" : multicolors.__next__()
						},
						"emphasis":{
							"barBorderWidth":2,
							"barBorderColor":"#0000EE"
						}
					},
					"data":[]
				}
				serieschild["name"] = ':'.join([parent,item[-30:]])
				serieschild["data"] = value
				serieschild["stack"] = parent
				series.append(serieschild)
				customs.append(serieschild['name'])
		elif len(child) == 1:
			serieschild = {
				"type":"bar",
				"itemStyle":{
					"normal" : {
						"color" : singlecolors.__next__()
					},
					"emphasis":{
						"barBorderWidth":2,
						"barBorderColor":"#0000EE"
					}
				},
				"data":[]
			}
			serieschild["name"] = ':'.join([parent,list(child.keys())[0][-10:]])
			serieschild["data"] = child[list(child.keys())[0]]
			series.append(serieschild)
			customs.append(serieschild["name"])
		else:
			serieschild = {
				"type":"bar",
				"itemStyle":{
					"normal" : {
					},
					"emphasis":{
						"barBorderWidth":2,
						"barBorderColor":"#0000EE"
					}
				},
				"data":[]
			}
			serieschild["name"] = parent
			serieschild["data"] = 0
			series.append(serieschild)
			customs.append(parent)
			

	barchartData = {
		"customs": customs,
		"xAxisData":[job.serviceversion for job in jobs],
		"series":series
	}

	return barchartData

@main.route('/getversion')
def getVersion(datadict=None):
	jobs = None
	datas = request.args if datadict is None else datadict
	
	servicetypes = []
	concurrents = []
	suits = []

	try:
		servicetypes = [(i,v.typename) for i,v in enumerate(Servicetype.query.all())]
		concurrents = [(j,k.concurrent) for j,k in enumerate(Job.query.group_by(Job.concurrent).all())]
		suits = [(l,m.name) for l,m in enumerate(Testsuit.query.all())]

		for i,v in servicetypes:
			if i == int(datas.get('type')):
				jobs = Job.query.filter_by(servicetype=v).filter_by(status=2)
				break

		for k,l in concurrents:
			if k == int(datas.get('conc')):
				jobs = jobs.filter_by(concurrent=l)
				break

		for m,n in suits:
			if m == int(datas.get('suit')):
				jobs = jobs.filter_by(relatesuitname=n).all()
				break
	except:
		errorinfo = traceback.format_exc()
		logging.error("数据库异常："+errorinfo)
		return [] if datadict is not None else JSONEncoder().encode([])

	if datadict is None:
		versions = [i.serviceversion for i in jobs]
		return JSONEncoder().encode(versions)
	else:
		selects = datadict.get('selects') if len(datadict.get('selects')) <= 10 else datadict.get('selects')[-10:]
		jobs = [job for index,job in enumerate(jobs) if str(index) in selects]
		return jobs
