from flask import render_template, session, request, redirect, url_for, abort
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from app.main import main
from app.stepic import stepic
from app.stepic.stepic_api import StepicOauth, StepicApi
from app.stepic.models import StepicTeacher, User, Course, Comment, Review

COMMENTS_PER_PAGE = 5
COMMENT_SORT_PARAMS = [
	{'value': 'reply_count', 'label': 'Ответы'},
	{'value': 'user_reputation', 'label': 'Репутация'},
	{'value': 'epic_count', 'label': 'Лайки'},
	{'value': 'abuse_count', 'label': 'Дизлайки'},
	{'value': 'time', 'label': 'Дата'}]
COMMENT_ORDER_PARAMS = [
	{'value': '', 'label': 'По возрастанию'},
	{'value': '-', 'label': 'По убыванию'}]
REVIEW_SORT_PARAMS = [
	{'value': 'user_reputation', 'label': 'Репутация'},
	{'value': 'score', 'label': 'Оценка'},
	{'value': 'create_date', 'label': 'Дата'}]

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


@stepic.route('/logout/', methods=['GET'])
@login_required
@stepic_login_required
def logout():
	logout_user()

	return redirect(url_for('main.index'))


@stepic.route('/authorization/', methods=['GET', 'POST'])
def authorization():
	if request.args.get('code') is None:
		abort(404)

	response = stepic_oauth.app.authorized_response()
	session['token'] = response['access_token']
	user_profile = StepicApi(session['token']).get_current_user_profile()
	stepic_id = user_profile['id']
	session['stepic_id'] = stepic_id
	StepicTeacher.objects(stepic_id=stepic_id).update_one(
		full_name=user_profile['full_name'],
		avatar_url=user_profile['avatar'],
		upsert=True)
	teacher = StepicTeacher.objects(stepic_id=stepic_id).first()
	login_user(teacher)

	return redirect(url_for('.show_all_comments'))


# ********** COMMENTS **********
@stepic.route('/comments/', methods=['GET'])
@stepic.route('/comments/<int:page>/', methods=['GET'])
@login_required
@stepic_login_required
def show_all_comments(page=1):
	comment_list = current_user.filter_and_sort_comments().paginate(page=page, per_page=COMMENTS_PER_PAGE)
	for comment in comment_list.items:
		comment.user.update_course_grades(session['token']).save()

	return render_template("stepic/comments.html", comment_list=comment_list, sort_select_list=COMMENT_SORT_PARAMS, order_select_list=COMMENT_ORDER_PARAMS)


@stepic.route('/comments/', methods=['POST'])
@login_required
@stepic_login_required
def update_comments_filtration():
	form = request.form
	current_user.update_comment_filters(form).save()

	return redirect(url_for('.show_all_comments'))


@stepic.route('/comments/update/', methods=['GET'])
@login_required
@stepic_login_required
def update_comments():
	stepic_api = StepicApi(session['token'])
	# update all comments
	for course in current_user.course_list:
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
				new_comment = Comment(user=user, user_reputation=user.reputation, course=course).update_comment(comment_info).save()
	# update all users
	user_id_list = User.objects().distinct('stepic_id')
	user_list = stepic_api.get_users_info(user_id_list)
	for user_info in user_list:
		User.objects(stepic_id=user_info['id']).first().update_user(user_info).save()

	return redirect(url_for('.show_all_comments'))


@stepic.route('/stepic_comment/<int:step_id>/<int:comment_id>/', methods=['GET'])
@login_required
@stepic_login_required
def show_comment(step_id, comment_id):
	stepic_api = StepicApi(session['token'])
	step_info = stepic_api.get_step_info(step_id)
	comment_url = 'https://stepik.org/lesson/{}/step/{}?discussion={}'.format(step_info['lesson'], step_info['position'], comment_id)

	return redirect(comment_url)


# ********** COURSES **********
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
	stepic_api = StepicApi(session['token'])
	course_list = stepic_api.get_user_courses(session['stepic_id'])
	for course_info in course_list:
		course = Course.objects(stepic_id=course_info.get('stepic_id')).first()
		if not course:
			course = Course(stepic_id=course_info.get('stepic_id'))
			current_user.course_list.append(course)
		course.update_course(course_info).save()
	current_user.save()

	return redirect(url_for('.show_all_courses'))


# ********** COURSE-REVIEWS **********
@stepic.route('/reviews/', methods=['GET'])
@stepic.route('/reviews/<int:page>/', methods=['GET'])
@login_required
@stepic_login_required
def show_all_reviews(page=1):
	review_list = current_user.filter_and_sort_reviews().paginate(page=page, per_page=COMMENTS_PER_PAGE)
	for review in review_list.items:
		review.user.update_course_grades(session['token']).save()

	return render_template("stepic/reviews.html", review_list=review_list, sort_select_list=REVIEW_SORT_PARAMS, order_select_list=COMMENT_ORDER_PARAMS)


@stepic.route('/reviews/', methods=['POST'])
@login_required
@stepic_login_required
def update_reviews_filtration():
	form = request.form
	current_user.update_review_filters(form).save()

	return redirect(url_for('.show_all_reviews'))


@stepic.route('/reviews/update/', methods=['GET'])
@login_required
@stepic_login_required
def update_reviews():
	stepic_api = StepicApi(session['token'])
	# update all reviews
	for course in current_user.course_list:
		review_list = stepic_api.get_course_reviews(course.stepic_id)
		for review_info in review_list:
			old_review = Review.objects(stepic_id=review_info['stepic_id']).first()
			if old_review:
				old_review.update_review(review_info).save()
			else:
				user = User.objects(stepic_id=review_info['user_id']).first()
				if not user:
					user = User(stepic_id=review_info['user_id']).save()
				user = user.add_course(review_info).save()
				new_review = Review(user=user, user_reputation=user.reputation, course=course).update_review(review_info).save()
	# update all users
	user_id_list = User.objects().distinct('stepic_id')
	user_list = stepic_api.get_users_info(user_id_list)
	for user_info in user_list:
		User.objects(stepic_id=user_info['id']).first().update_user(user_info).save()

	return redirect(url_for('.show_all_reviews'))


@stepic.route('/stepic_review/<int:review_id>/', methods=['GET'])
@login_required
@stepic_login_required
def show_review(review_id):
	review = Review.objects(stepic_id=review_id).first()
	review_url = 'https://stepik.org/course/{}/reviews/{}'.format(review.course.stepic_id, review.stepic_id)

	return redirect(review_url)
