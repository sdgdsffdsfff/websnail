from threading import Thread
import time,json
import math
from collections import Counter,OrderedDict
import sys
class Report(object):
	def __init__(self,id,logpath,url,reportfile):
		self.id = id
		self.logpath = logpath
		self.url = url
		self.report = OrderedDict() 
		self.reportfile = reportfile

	def generateReport(self):
		result = Results(self.logpath)
		span_list=[]
		elapsed_list=[]
		for i in result.status_list:
			span_list.append(i.time_span)
			elapsed_list.append(i.elapsed)
		average=float(sum(span_list)/result.total_num)
		max_span=max(span_list)
		min_span=min(span_list)
		elapsed_time=max(elapsed_list)
		if elapsed_time!=elapsed_list[-1]:
			print (elapsed_time,elapsed_list[-1])
			print ('ERROR:SPAWN')
			#sys.exit(1)
		throught=float(result.total_num/elapsed_time)
		self.report['logpath'] = self.logpath
		self.report['totalrequests'] = result.total_num
		self.report['averagetime'] = round(average,3)
		self.report['throught'] = round(throught,2)
		self.report['min_span'] = round(min_span,3)
		self.report['max_span'] = round(max_span,3)
		self.report['errorcount'] = result.error_num
		self.report['errorcounter'] = {}
		self.report['customtimers'] = {}
		self.report['customscore'] = {}
		print ('url: %s '%(self.url))
		print ('logpath: %s'%(self.logpath))
		print ('Total requests: %d'%(result.total_num))
		print ('average: %.3f throught: %.2f'%(average,throught))
		print ('max: %.3f min: %.3f\n'%(max_span,min_span))
		print ('Error: %s (%.3f%%)' %(result.error_num,result.error_num*100/result.total_num))
		if result.error_num:
			for k,v in dict(result.error_counter).items():
				self.report['errorcounter'][k] = v
				#print ('--> %s: %s (%.3f%%)'%(k,v,v*100/result.total_num))
		if result.counter:
			#print ('==Custom timers: ')
			for k,v in result.counter.items():
				self.report['customtimers'][k] = {}#
				#print ('--> %s: %s (%.3f%%)'%(k,sum(dict(v).values()),sum(dict(v).values())*100/result.total_num))
				for k2,v2 in dict(v).items():
					self.report['customtimers'][k][k2] = v2	
					#print ('%s: %s (%.3f%%)'%(k2,v2,v2*100/result.total_num))
		if result.score:
			#print ('\n==Custom Score')
			for k,v in result.score.items():
				self.report['customscore'][k] = v#
				#print ('Average %s : %.3f'%(k,v/result.total_num))
		
		with open(self.reportfile,'w') as f:
			json.dump(self.report,f)

class Results():
	def __init__(self,logpath):
		self.logpath = logpath
		self.total_num=0
		self.error_num=0
		self.counter={}
		self.error_counter=Counter()
		self.score={}
		self.status_list=self.__parse_file()
		
	def __parse_file(self):
		print("Results.logpath:",self.logpath)
		f = open(self.logpath,'rb')
		status_list=[]
		for line in f:
			fields=line.decode().strip().replace(' ','').split(',')
			total_num=int(fields[0])
			elapsed_time=float(fields[1])
			pt_name=fields[2]
			time_span=float(fields[3])
			err_num=int(fields[4])
			try:
				custom=eval(','.join(fields[6:]))
			except Exception as e:
				print (str(e))
				return
			for k,v in custom.items():
				if k=='error':
					self.error_num+=1
					if len(v)>100:
						if v.find('connecttimeout'):
							self.error_counter.update({v[-30:-3]})
						else:
							self.error_counter.update({'Unknown'})
					else:
						self.error_counter.update({str(v)})
					break
				elif  k.startswith('c_'):
					if self.counter.get(k) is None:
						self.counter[k]=Counter()
					self.counter[k].update({str(v)})
				elif k.startswith('t_'):
					if self.score.get(k) is None:
						self.score[k]=v
					else:
						self.score[k]+=v
				else:
					continue
			r=ResponseStats(total_num,elapsed_time,pt_name,time_span,err_num,custom)
			self.total_num+=1
			status_list.append(r)
		return status_list
		#print ('IP: %s Concurrent: %d Total Requests: %d Total Time: %.2f'%(self.ip,request_num,))
		#print 
			
		
class ResponseStats():
	def __init__(self,total_num,elapsed,pt_name,time_span,err_num,custom):
		self.total_num=total_num
		self.elapsed=elapsed
		self.pt_name=pt_name
		self.time_span=time_span
		self.err_num=err_num
		self.custom=custom
	
class tracker(Thread):
	def __init__(self,writter):
		Thread.__init__(self)
		self.w=writter
		self.turn=True
	def run(self):
		total_temp=0
		error_temp=0
		elapsed_temp=0
		alltime_temp=0
		time.sleep(2)
		while self.turn:
			total_span,error_span,elapsed_span,alltime_span=self.w.total_c-total_temp,self.w.error_c-error_temp,self.w.elapsed-elapsed_temp,self.w.all_time-alltime_temp
			total_temp=self.w.total_c
			error_temp=self.w.error_c
			elapsed_temp=self.w.elapsed
			alltime_temp=self.w.all_time
			if elapsed_span==0 or elapsed_temp==0:
				time.sleep(1)
				continue
			print ("%s %s in %s = %s/s Avg: %s Err: %s"%("summary + ",str(total_span).rjust(7,' '),str(round(elapsed_span,3)).rjust(7,' '),str(round(total_span/elapsed_span,2)).rjust(6,' '),str(round(alltime_span/total_span,3)).rjust(6,' '),str(error_span).rjust(5,' ')))
			print ("%s %s in %s = %s/s Avg: %s Err: %s"%("summary = ",str(total_temp).rjust(7,' '),str(round(elapsed_temp,3)).rjust(7,' '),str(round(total_temp/elapsed_temp,2)).rjust(6,' '),str(round(self.w.average,3)).rjust(6,' '),str(error_temp).rjust(5,' ')))
			time.sleep(10)


class processbar():
	def __init__(self,duration):
		self.duration=duration
		self.prog_bar='[]'
		self.fill_char='='
		self.width=80
		self.percent_done = 0
		self.__update_amount(0)

	def __update_amount(self, new_amount):
		self.percent_done = int(math.floor((new_amount / 100.0) * 100.0))
		if self.percent_done > 100:
			self.percent_done = 100
		all_full = self.width - 2
		num_hashes = int(round((self.percent_done / 100.0) * all_full))
		self.prog_bar = '[' + self.fill_char * num_hashes + ' ' * (all_full - num_hashes) + ']'
		pct_place = (len(self.prog_bar) // 2) - len(str(self.percent_done))
		pct_string = '%i%%' % self.percent_done
		self.prog_bar = self.prog_bar[0:pct_place] + (pct_string + self.prog_bar[pct_place + len(pct_string):])

	def update_time(self, elapsed_secs):
		self.__update_amount((elapsed_secs / float(self.duration)) * 100.0)
		self.prog_bar += '  %d/%s' % (elapsed_secs, self.duration)

	def __str__(self):
		return str(self.prog_bar)
	
	def getProgress(self):
		return(self.percent_done)


if __name__=='__main__':
	report('/home/wenba/xz/automation/snail/log/2015-04-24_10-18-26.log','asd')


