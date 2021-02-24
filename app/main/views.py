from datetime import date, timedelta
from app.main import main
from flask import request, render_template, redirect, url_for, jsonify
from flask_login import current_user


@main.route('/favicon.ico/')
def favicon():
	return redirect(url_for('static', filename='images/favicon.ico'))


@main.route('/', methods=['GET'])
def index():
	return render_template("main/index.html")


@main.route('/get_date_interval/', methods=['POST'])
def get_date_interval():
	day_count = request.json.get('day_count')
	date_from = (date.today() - timedelta(int(day_count))).isoformat()
	date_to = (date.today() + timedelta(1)).isoformat()

	return jsonify(date_from=date_from, date_to=date_to)
