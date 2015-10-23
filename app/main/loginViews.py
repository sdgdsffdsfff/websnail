from flask import request,render_template,flash,redirect,url_for
from datetime import datetime
from json import JSONEncoder
from . import main
from .forms import LoginForm,RegisterForm
from ..models import db,User
from werkzeug.security import generate_password_hash,check_password_hash
from flask.ext.login import login_user,logout_user

@main.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm()
	if request.method == 'POST' and form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if check_password_hash(user.password,form.password.data):
			login_user(user)
			return redirect(url_for('.testjobs'))
		else:
			flash({"type":"error","message":"用户名或密码不存在！"})
			
	return render_template('login.html',form=form)

@main.route('/register',methods=['GET','POST'])
def register():
	form = RegisterForm()
	if request.method == 'POST' and form.validate_on_submit():
		user = User(
			email = request.form['email'],
			password = generate_password_hash(request.form['password'])
		)	
		db.session.add(user)
		db.session.commit()
		flash({"type":"info","message":"注册成功！"})
		return redirect(url_for('.login'))
	return render_template('register.html',form=form)

@main.route('/logout')
def logout():
	logout_user()
	flash({"type":"info","message":"成功登出！"})
	return redirect(url_for('main.login'))


if __name__ == '__main__':
	url = "http://wb-img.u.qiniudn.com/"
	#url = "http://wb-img.u.qiniudn.com/20150426-7c097ab4-155d-4e32-baa8-abbb7a71b567.png"
	#url = "20150426-B0407B5E-98E2-4385-970A-30F4787F5F63.jpg"
	print(reviseUrl(url))
