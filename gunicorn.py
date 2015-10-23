import os,multiprocessing
bind = "0.0.0.0:8888"
workers = multiprocessing.cpu_count()*2 + 1
worker_class = "sync"
backlog = 2048
reload = True
debug = True
#accesslog = "/data/websnail/logs/gunicorn/access.log"
#access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
#errorlog = "/data/websnail/logs/gunicorn/error.log"
#logfile = "/data/websnail/logs/gunicorn/debug.log"
#loglevel = "info"


