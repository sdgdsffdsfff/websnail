from flask_wtf import Form
from wtforms import FloatField,IntegerField,StringField,SubmitField,TextAreaField,TextField,SelectField,FileField,SelectMultipleField,BooleanField,PasswordField
from wtforms import validators,ValidationError
from flask.ext.codemirror.fields import CodeMirrorField
from ..models import User

class LoginForm(Form):
	email = StringField("邮箱地址:",[validators.Required()])
	password = PasswordField('密码:',[validators.Required()])
	submit = SubmitField("提交")

class RegisterForm(Form):
	email = StringField("邮箱地址:",[validators.Required()])
	password = PasswordField('密码:',[validators.Required()])
	confirmpass = PasswordField('确认密码:',[validators.EqualTo('password',message='两次密码输入不一致')])
	submit = SubmitField("提交")

	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError("该邮箱已注册")


class JobForm(Form):
	service = SelectField('测试接口:',coerce=int,default=1)
	selectfile = SelectField('测试脚本:',coerce=int,default=1)
	suits = SelectField('选择测试集:',coerce=int)
	serviceversion = StringField("接口版本号:",[validators.Required()])
	concurrent = IntegerField('并发量:',[validators.Required("请输入整数！"),validators.NumberRange(1,5000,"请输入1~1000范围内的整数！")])
	run_time = IntegerField('并发时间:(秒)',[validators.Optional(True),validators.NumberRange(min=0,message="请输入正整数！")])
	run_num = IntegerField('循环次数:',[validators.Optional(True),validators.NumberRange(min=0,message="请输入正整数！")])
	submit = SubmitField('提交测试')

class TSForm(Form):
	ip = StringField('请求地址:',[validators.Required()])
	path = StringField('路径:')
	connect_timeout = FloatField('连接超时(秒):',[validators.Optional(True),validators.NumberRange(0,1000,"请输入1~1000范围内的整数！")])
	response_timeout = FloatField('响应超时(秒):',[validators.Optional(True),validators.NumberRange(0,1000,"请输入1~1000范围内的整数！")])
	method = SelectField('方法:',choices=[('post','POST'),('get','GET')],default=1)
	need_headers = BooleanField('需要修改数据类型(默认:{"content-type":"text/html"} )')
	headers = StringField('headers:(请按需修改)')
	data = CodeMirrorField('请求数据(json格式，例：{"orderID":12,"orderTime":"1440060000"})',
				language='html',
				config={'lineNumbers':'true','lineWrapping':'true','smartIndent':'true'}
			)
	returnfield = StringField('返回字段Counter:')
	
class AnalysisForm(Form):
	servicetype = SelectField('服务类型:',coerce=int,default=1)
	concurrent = SelectField('并发量:',coerce=int,default=1)
	suit = SelectField('测试集:',coerce=int,default=1)
	serviceversion = SelectMultipleField('选择版本',choices=[])
	submit = SubmitField("确定")

class ServiceForm(Form):
	name = StringField('接口名称:',[validators.Required()])
	address = StringField('接口地址:',[validators.Required()])
	submit = SubmitField("保存")

class TestSuitForm(Form):
	name = StringField('测试集名称:',[validators.Required("需要输入内容")])
	servicetype = SelectField('服务类型:',coerce=int,default=1)
	filename = FileField("选择文件:")
	datafile = StringField("数据文件路径:")
	submit = SubmitField("保存")

class ScriptForm(Form):
	content = CodeMirrorField('脚本内容:',
				language='python',
				config={'lineNumbers':'true','lineWrapping':'true','indentUnit':10}
			)
	scriptname = StringField('脚本名称:',[validators.Required("脚本名称必填！"),validators.Regexp(r".+(.py)$",message="脚本名称必须以.py结尾")])
	desc = TextField('脚本描述:',[validators.Required()])
	submit = SubmitField('保存')

class FileForm(Form):
	filename = FileField("选择文件:",[validators.Required()])
	directory = StringField("存放路径:",[validators.Required("请输入存放路径！")],default="/data/websnail/resources/uploads")
	concurrent = IntegerField("下载线程数:",[validators.Required("请输入数字！"),validators.NumberRange(1,1000,"请输入1~1000范围内的整数！")])
	submit = SubmitField("开始下载")

if __name__ == '__main__':
	print('ok')
