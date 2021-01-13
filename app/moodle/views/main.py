from flask import request, redirect, url_for, abort
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
		return redirect(url_for('.show_all_courses'))

	return redirect(url_for('moodle.authorization'), code=308)


@moodle.route('/authorization/', methods=['POST'])
def authorization():
	form = request.form
	moodle_auth = MoodleAuth(form)
	token = moodle_auth.get_user_token()
	if not token:
		return redirect(url_for('main.index'))
	moodle_url = moodle_auth.get_moodle_url()
	teacher_info = MoodleApi(moodle_url, token).get_current_user_profile()
	teacher = MoodleTeacher.objects(moodle_id=teacher_info.get('userid')).modify(
		moodle_id=teacher_info.get('userid'),
		moodle_url=moodle_url,
		token=token,
		upsert=True,
		new=True)
	teacher.update_teacher(teacher_info).save()
	login_user(teacher)

	return redirect(url_for('.show_all_courses'))


@moodle.route('/logout/', methods=['GET'])
@login_required
@moodle_login_required
def logout():
	logout_user()

	return redirect(url_for('main.index'))
