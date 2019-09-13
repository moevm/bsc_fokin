from app.main import main
from flask import render_template, session, request, redirect, url_for, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.main.stepic import StepicOauth, StepicAgent, StepicApi
from app.main.models import Teacher, Course

stepic_oauth = StepicOauth()


@main.route('/login/', methods=['GET', 'POST'])
def login():
	return stepic_oauth.app.authorize(callback=url_for('.authorization', _external=True))


@main.route('/logout/', methods=['GET'])
@login_required
def logout():
	logout_user()
	return redirect(url_for('.index'))


@main.route('/authorization/', methods=['GET', 'POST'])
def authorization():
	if request.args.get('code') is None:
		abort(404)

	response = stepic_oauth.app.authorized_response()
	session['token'] = response['access_token']
	stepic_agent = StepicAgent(session['token'])
	stepic_id, full_name, avatar_url = stepic_agent.get_profile_info()
	Teacher.objects(stepic_id=stepic_id).update_one(
		full_name=full_name,
		avatar_url=avatar_url,
		upsert=True)
	teacher = Teacher.objects(stepic_id=stepic_id).first()
	login_user(teacher)

	return redirect(url_for('.show_all_courses'))


@main.route('/', methods=['GET'])
def index():
	if current_user.is_authenticated:
		return redirect(url_for('.show_all_courses'))
	else:
		return render_template("main/index.html")


@main.route('/courses/', methods=['GET'])
@login_required
def show_all_courses():
	courses = Course.objects()

	return render_template("main/courses.html", courses=courses)
