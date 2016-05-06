from flask import render_template,redirect,url_for,flash
from ..models import Report,Job,Testsuit,Service,Script
from . import main
from collections import OrderedDict
from .Public import logging
import traceback

@main.route('/viewreport/<id>')
def view(id):
    report = None
    job = None
    suit = None
    try:
        report = Report.query.filter_by(jobid=id).order_by(Report.id.desc()).first()
        job = Job.query.filter_by(id=report.jobid).first()
    except:
        errorinfo = traceback.format_exc()
        logging.error("数据库异常：" + errorinfo)
        flash({"type":"error","message":"数据库异常！"})
        return render_template('dberror.html',errorinfo=errorinfo.split('\n'))

    if report is not None:
        reportDetail = OrderedDict()
        reportDetail['接口名称'] = job.servicename
        reportDetail['接口地址'] = job.address
        reportDetail['测试脚本'] = job.filename
        reportDetail['并发数'] = job.concurrent
        reportDetail['测试时间'] = job.createdtime
        reportDetail['日志路径'] = report.logpath
        reportDetail['总请求数'] = report.totalrequests
        reportDetail['平均响应时间and吞吐量'] = "{average}秒 | {throught}".format(average=report.averagetime,throught=report.throught)
        reportDetail['最小and最大响应时间'] = "{min}秒 - {max}秒".format(min=report.min_span,max=report.max_span)
        reportDetail['错误请求数及占比'] = "{e_c}个  占比:{percent}%".format(e_c=report.errorcount,percent=round(report.errorcount*100/report.totalrequests,3))
        reportDetail['错误统计ErrorCounter'] = report.errorcounter
        customs = []
        for i,v in report.customtimers.items():
            custom = '[' + i + ']' + '\t\t' 
            child = ''
            for j,x in v.items():
                child += ''.join([j,':',str(x),'(',str(round(x*100/report.totalrequests,3)),'%',')',' ']) 
            customs.append(custom+child)
        reportDetail['参数计数器CustomTimers'] = '\n'.join(customs)
    else:
        logging.error("报告不存在！")
        return render_template('404.html'),404
    return(render_template('report.html',reportDetail=reportDetail))

