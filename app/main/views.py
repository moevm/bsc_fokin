from app.main import main
from flask import render_template, session, request, redirect, url_for, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.main.stepic import StepicOauth, StepicApi
from app.main.models import Teacher, Course, Comment

COMMENTS_PER_PAGE = 5
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
	stepic_api = StepicApi(session['token'])
	user_profile = stepic_api.get_user_profile()
	stepic_id = user_profile['id']
	session['stepic_id'] = stepic_id
	Teacher.objects(stepic_id=stepic_id).update_one(
		full_name=user_profile['full_name'],
		avatar_url=user_profile['avatar'],
		upsert=True)
	teacher = Teacher.objects(stepic_id=stepic_id).first()
	login_user(teacher)

	return redirect(url_for('.show_all_comments'))


@main.route('/', methods=['GET'])
def index():
	if current_user.is_authenticated:
		return redirect(url_for('.show_all_comments'))
	else:
		return render_template("main/index.html")


@main.route('/comments/', methods=['GET', 'POST'])
@main.route('/comments/<int:page>/', methods=['GET', 'POST'])
@login_required
def show_all_comments(page=1):
	comment_list = Comment.objects.paginate(page=page, per_page=COMMENTS_PER_PAGE)

	return render_template("main/comments.html", comment_list=comment_list)


@main.route('/comments/update/', methods=['GET'])
@login_required
def update_comments():
	stepic_api = StepicApi(session['token'])
	for course in Course.objects():
		comment_list = stepic_api.get_course_comments(course.stepic_id)
		for comment in comment_list:
			Comment.objects(stepic_id=comment['stepic_id']).update_one(
				parent_id = comment['parent_id'],
				step_id = comment['step_id'],
				user_id = comment['user_id'],
				user_role = comment['user_role'],
				time = comment['time'],
				last_time = comment['last_time'],
				text = comment['text'],
				replies = comment['replies'],
				reply_count = comment['reply_count'],
				is_deleted = comment['is_deleted'],
				is_pinned = comment['is_pinned'],
				is_staff_replied = comment['is_staff_replied'],
				is_reported = comment['is_reported'],
				attachments = comment['attachments'],
				epic_count = comment['epic_count'],
				abuse_count = comment['abuse_count'],
				upsert=True)

	return redirect(url_for('.show_all_comments'))


@main.route('/courses/', methods=['GET'])
@login_required
def show_all_courses():
	course_list = Course.objects()

	return render_template("main/courses.html", course_list=course_list)


@main.route('/courses/update/', methods=['GET'])
@login_required
def update_courses():
	stepic_api = StepicApi(session['token'])
	course_list = stepic_api.get_user_courses(session['stepic_id'])
	for course in course_list:
		Course.objects(stepic_id=course['stepic_id']).update_one(
			stepic_id=course['stepic_id'],
			title=course['title'],
			summary=course['summary'],
			cover=course['cover'],
			cert_reg_threshold=course['cert_reg_threshold'],
			cert_dist_threshold=course['cert_dist_threshold'],
			score=course['score'],
			upsert=True)

	return redirect(url_for('.show_all_courses'))
