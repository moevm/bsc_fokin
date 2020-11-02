from app.main import main
from flask import render_template, redirect, url_for
from flask_login import current_user


@main.route('/favicon.ico')
def favicon():
	return redirect(url_for('static', filename='images/favicon.ico'))


@main.route('/', methods=['GET'])
def index():
	# print('index', current_user.is_authenticated)

	return render_template("main/index.html")
