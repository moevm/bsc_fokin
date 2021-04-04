from flask import request, redirect, url_for, abort
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from app.main import main
from app.stepic import stepic
from app.stepic.stepic_api import StepicOauth, StepicApi
from app.stepic.models import StepicTeacher


stepic_oauth = StepicOauth()


def stepic_login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not current_user.is_stepic_teacher():
			return abort(401)
		return f(*args, **kwargs)
	return decorated_function


@stepic.route('/login/', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated and current_user.is_stepic_teacher():
		return redirect(url_for('.show_all_comments'))

	return stepic_oauth.app.authorize(callback=url_for('.authorization', _external=True))


@stepic.route('/authorization/', methods=['GET', 'POST'])
def authorization():
	if request.args.get('code') is None:
		abort(404)

	response = stepic_oauth.app.authorized_response()
	user_token = response['access_token']
	teacher_info = StepicApi(user_token).get_current_user_profile()
	teacher = StepicTeacher.objects(stepic_id=teacher_info.get('id')).modify(
		stepic_id=teacher_info.get('id'),
		token=user_token,
		upsert=True,
		new=True)
	teacher.update_teacher(teacher_info).save()
	login_user(teacher)

	return redirect(url_for('.show_all_courses'))


@stepic.route('/logout/', methods=['GET'])
@login_required
@stepic_login_required
def logout():
	logout_user()

	return redirect(url_for('main.index'))
