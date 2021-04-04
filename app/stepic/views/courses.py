from flask import render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.stepic import stepic
from app.stepic.stepic_api import StepicApi
from app.stepic.models import StepicCourse
from app.stepic.views.main import stepic_login_required


@stepic.route('/courses/', methods=['GET'])
@login_required
@stepic_login_required
def show_all_courses():
	course_list = current_user.course_list

	return render_template("stepic/courses.html", course_list=course_list)


@stepic.route('/courses/update/', methods=['GET'])
@login_required
@stepic_login_required
def update_courses():
	stepic_api = StepicApi(current_user.token)
	course_list = stepic_api.get_user_courses(current_user.stepic_id)
	user_course_list = []
	for course_info in course_list:
		course = StepicCourse.objects(stepic_id=course_info.get('stepic_id')).modify(
			stepic_id=course_info.get('stepic_id'),
			upsert=True,
			new=True)
		user_course_list.append(course)
		course.update_course(course_info).save()
	current_user.modify(course_list=user_course_list)

	return jsonify(redirect_url=url_for('.show_all_courses'))
