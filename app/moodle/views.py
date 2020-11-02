from flask import render_template, session, request, redirect, url_for, abort, flash
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from app.main import main
from app.moodle import moodle
from app.moodle.moodle_api import MoodleAuth, MoodleApi
from app.moodle.models import MoodleTeacher


def moodle_login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not current_user.is_moodle_teacher():
			return abort(401)
		return f(*args, **kwargs)
	return decorated_function


@moodle.route('/login/', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated and current_user.is_moodle_teacher():
		# return redirect(url_for('.show_all_comments'))
		return redirect(url_for('.show_all_courses'))

	return redirect(url_for('moodle.authorization'), code=308)


@moodle.route('/authorization/', methods=['POST'])
def authorization():
	form = request.form
	moodle_auth = MoodleAuth(form)
	token = moodle_auth.get_user_token()
	if not token:
		return redirect(url_for('main.index'))
	user_profile = MoodleApi(moodle_auth.get_site_url(), token).get_current_user_profile()
	MoodleTeacher.objects(moodle_id=user_profile['userid']).update_one(
		token=token,
		username=user_profile['username'],
		full_name=user_profile['fullname'],
		avatar_url=user_profile['userpictureurl'],
		upsert=True)
	teacher = MoodleTeacher.objects(moodle_id=user_profile['userid']).first()
	login_user(teacher)

	# return redirect(url_for('.show_all_comments'))
	return redirect(url_for('.show_all_courses'))


@moodle.route('/logout/', methods=['GET'])
@login_required
@moodle_login_required
def logout():
	logout_user()

	return redirect(url_for('main.index'))


# ********** COURSES **********
@moodle.route('/courses/', methods=['GET'])
@login_required
@moodle_login_required
def show_all_courses():
	course_list = []
	# course_list = current_user.course_list

	return render_template("moodle/courses.html", course_list=course_list)


@moodle.route('/courses/update/', methods=['GET'])
@login_required
@moodle_login_required
def update_courses():
	# stepic_api = StepicApi(session['token'])
	# course_list = stepic_api.get_user_courses(session['stepic_id'])
	# for course_info in course_list:
	# 	course = Course.objects(stepic_id=course_info['stepic_id']).first()
	# 	if not course:
	# 		course = Course()
	# 		current_user.course_list.append(course)
	# 	course.update_course(course_info).save()
	# current_user.save()

	return redirect(url_for('.show_all_courses'))


# ********** COURSES **********
