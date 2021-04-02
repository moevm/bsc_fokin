from app.main import main
from flask import render_template, redirect, url_for


@main.route('/favicon.ico/')
def favicon():
	return redirect(url_for('static', filename='images/favicon.ico'))


@main.route('/', methods=['GET'])
def index():
	return render_template("main/index.html")
