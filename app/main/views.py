from app.main import main
from flask import render_template, session, request, redirect, url_for, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.main.stepic import StepicOauth, StepicAgent, StepicApi
from app.main.spreadsheet import GSpread
from app.main.models import Teacher, Course, Group
import time

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
	token = response['access_token']
	session['token'] = token
	stepic_agent = StepicAgent(token)
	full_name, avatar_url, stepic_id = stepic_agent.get_profile_info()

	teacher = Teacher.objects(stepic_id=stepic_id).first()
	if teacher is None:
		return redirect(url_for('.index'))
	else:
		teacher.full_name = full_name
		teacher.avatar_url = avatar_url
		teacher.save()
		login_user(teacher)
		return redirect(url_for('.show_all_courses'))


@main.route('/', methods=['GET'])
def index():
	if current_user.is_authenticated:
		return redirect(url_for('.show_all_courses'))
	else:
		return render_template("main/index.html")


# ******************************************************************************
# Преподаватели
# ******************************************************************************
@main.route('/teachers/', methods=['GET'])
@login_required
def show_all_teachers():
	teachers = Teacher.objects()

	return render_template("main/teachers.html", teachers=teachers)


@main.route('/teachers/add_teacher/', methods=['POST'])
@login_required
def add_new_teacher():
	post_data = request.json
	user_id = post_data['user_id']

	if not Teacher.objects(stepic_id=user_id):
		stepic_api = StepicApi()
		new_teacher = stepic_api.get_teacher_info(user_id)
		new_teacher.save()

	return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@main.route('/teachers/delete/<string:serial_id>/', methods=['GET'])
@login_required
def delete_teacher(serial_id):
	Teacher.objects(serial_id=serial_id).delete()

	return redirect(url_for('.show_all_teachers'))


# ******************************************************************************
# Курсы
# ******************************************************************************
@main.route('/courses/', methods=['GET'])
@login_required
def show_all_courses():
	courses = Course.objects()

	return render_template("main/courses.html", courses=courses)


@main.route('/courses/add_course/', methods=['POST'])
@login_required
def add_new_course():
	post_data = request.json
	course_id = post_data['course_id']

	if not Course.objects(stepic_id=course_id):
		stepic_api = StepicApi()
		new_course = stepic_api.get_course_info(course_id)
		new_course.save()

	return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@main.route('/courses/delete/<string:serial_id>/', methods=['GET'])
@login_required
def delete_course(serial_id):
	course = Course.objects(serial_id=serial_id).first()
	Group.objects(course_id=course.stepic_id).delete()
	Course.objects(serial_id=serial_id).delete()

	return redirect(url_for('.show_all_courses'))


@main.route('/course/', methods=['POST'])
@login_required
def show_course_info():
	post_data = request.json
	course_serial = post_data['course_serial']

	course = Course.objects(serial_id=course_serial).first()
	group_list = Group.objects(course_id=course.stepic_id)

	return jsonify({'success': True, 'course': course, 'group_list': group_list}), 200, {
		'ContentType': 'application/json'}


# ******************************************************************************
# Группы
# ******************************************************************************
@main.route('/course/add_groups/', methods=['POST'])
@login_required
def add_new_groups():
	post_data = request.json
	course_id = post_data['course_id']
	class_id = post_data['class_id']
	spreadsheet_key = post_data['spreadsheet_key']

	stepic_api = StepicApi()
	gspread = GSpread(spreadsheet_key)
	group_dict = gspread.get_groups()
	for group_title in group_dict.keys():
		group = Group.objects(course_id=course_id, title=group_title).first()
		if not group:
			group = Group(course_id=course_id, class_id=class_id, title=group_title)

		student_dict = {
			student[2]: {
				'full_name': '{1} {0}'.format(*student),
				'student_id': student[3]
			}
			for student in group_dict[group_title]}

		if class_id == '':
			group_info = stepic_api.get_group_info(
				course_id,
				student_dict)
		else:
			group_info = stepic_api.get_group_info_by_class(
				course_id,
				class_id,
				student_dict)

		group.students = group_info['students']
		group.learners = group_info['learners']
		group.cert_reg = group_info['cert_reg']
		group.cert_dist = group_info['cert_dist']
		group.certificates = group_info['cert_reg'] + group_info['cert_dist']
		group.steps = group_info['steps']
		group.labs = group_info['labs']
		group.save()

	return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@main.route('/groups/delete/<string:serial_id>/', methods=['GET'])
@login_required
def delete_group(serial_id):
	Group.objects(serial_id=serial_id).delete()

	return redirect(url_for('.show_all_courses'))


@main.route('/groups/<string:serial_id>/', methods=['GET'])
@login_required
def show_group_info(serial_id):
	group = Group.objects(serial_id=serial_id).first()
	if not group:
		abort(404)
	course = Course.objects(stepic_id=group.course_id).first()

	return render_template("main/group_info.html", course=course, group=group)


@main.route('/groups/<string:serial_id>/first_solutions/', methods=['POST'])
@login_required
def get_first_course_solutions(serial_id):
	post_data = request.json
	user_id = post_data['user_id']

	stepic_api = StepicApi()
	group = Group.objects(serial_id=serial_id).first()
	if not group:
		abort(404)
	course = Course.objects(stepic_id=group.course_id).first()
	
	dates = stepic_api.get_first_solution_dates(user_id, course.steps)
	group.students[user_id]['first_solution'] = dates['first_solution']
	group.students[user_id]['first_correct_solution'] = dates['first_correct_solution']
	group.students[user_id]['solutions_update'] = time.ctime()
	group.save()
	dates['solutions_update'] = group.students[user_id]['solutions_update']
	
	return jsonify({'success': True, 'dates': dates}), 200, {'ContentType': 'application/json'}


@main.route('/groups/<string:serial_id>/lab/<string:stepic_id>/', methods=['GET'])
@login_required
def show_lab_info(serial_id, stepic_id):
	group = Group.objects(serial_id=serial_id).first()
	if not group:
		abort(404)

	return render_template("main/lab_info.html", group=group, lesson_id=stepic_id)


@main.route('/groups/<string:serial_id>/lab/<string:stepic_id>/first_solutions/', methods=['POST'])
@login_required
def get_first_lab_solutions(serial_id, stepic_id):
	post_data = request.json
	user_id = post_data['user_id']

	stepic_api = StepicApi()
	group = Group.objects(serial_id=serial_id).first()
	if not group:
		abort(404)

	step_id = group.students[user_id]['labs'][stepic_id]['step_id']
	dates = stepic_api.get_first_solution_dates(user_id, [step_id])
	group.students[user_id]['labs'][stepic_id]['first_solution'] = dates['first_solution']
	group.students[user_id]['labs'][stepic_id]['first_correct_solution'] = dates['first_correct_solution']
	group.students[user_id]['labs'][stepic_id]['solutions_update'] = time.ctime()
	group.save()
	dates['solutions_update'] = group.students[user_id]['labs'][stepic_id]['solutions_update']
	
	return jsonify({'success': True, 'dates': dates}), 200, {'ContentType': 'application/json'}
