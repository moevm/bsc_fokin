from app.main import main
from flask import render_template, session, request, redirect, url_for, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.main.stepic import StepicOauth, StepicApi
from app.main.models import Teacher, User, Course, Comment

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
	user_profile = stepic_api.get_current_user_profile()
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
	comment_list = Comment.objects.order_by('-epic_count').paginate(page=page, per_page=COMMENTS_PER_PAGE)

	return render_template("main/comments.html", comment_list=comment_list)


@main.route('/comments/update/', methods=['GET'])
@login_required
def update_comments():
	stepic_api = StepicApi(session['token'])
	# update all comments
	for course in Course.objects:
		comment_list = stepic_api.get_course_comments(course.stepic_id)
		for comment_info in comment_list:
			old_comment = Comment.objects(stepic_id=comment_info['stepic_id']).first()
			if old_comment:
				old_comment.update_comment(comment_info).save()
			else:
				user = User.objects(stepic_id=comment_info['user_id']).first()
				if not user:
					user = User(stepic_id=comment_info['user_id'])
				user = user.add_step(comment_info).save()
				new_comment = Comment().add_comment(comment_info, user).save(validate=False)
	# update all users
	user_id_list = User.objects().distinct('stepic_id')
	user_list = stepic_api.get_users_info(user_id_list)
	for user_info in user_list:
		User.objects(stepic_id=user_info['id']).first().update_user(user_info).save()

	return redirect(url_for('.show_all_comments'))


@main.route('/courses/', methods=['GET'])
@login_required
def show_all_courses():
	course_list = Course.objects

	return render_template("main/courses.html", course_list=course_list)


@main.route('/courses/update/', methods=['GET'])
@login_required
def update_courses():
	stepic_api = StepicApi(session['token'])
	course_list = stepic_api.get_user_courses(session['stepic_id'])
	for course_info in course_list:
		course = Course.objects(stepic_id=course_info['stepic_id']).first()
		if not course:
			course = Course()
		course.update_course(course_info).save()

	return redirect(url_for('.show_all_courses'))
