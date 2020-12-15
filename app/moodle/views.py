from flask import render_template, request, redirect, url_for, abort
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from app.main import main
from app.moodle import moodle
from app.moodle.moodle_api import MoodleAuth, MoodleApi
from app.moodle.models import MoodleTeacher, MoodleCourse, MoodleForum, MoodleDiscussion

DISCUSSIONS_PER_PAGE = 5


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
		return redirect(url_for('.show_all_discussions'))

	return redirect(url_for('moodle.authorization'), code=308)


@moodle.route('/authorization/', methods=['POST'])
def authorization():
	form = request.form
	moodle_auth = MoodleAuth(form)
	token = moodle_auth.get_user_token()
	if not token:
		return redirect(url_for('main.index'))
	moodle_url = moodle_auth.get_moodle_url()
	user_profile = MoodleApi(moodle_url, token).get_current_user_profile()
	teacher = MoodleTeacher.objects(moodle_id=user_profile.get('userid')).modify(
		moodle_url=moodle_url,
		token=token,
		username=user_profile.get('username'),
		full_name=user_profile.get('fullname'),
		user_picture_url=user_profile.get('userpictureurl'),
		upsert=True,
		new=True)
	login_user(teacher)

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
	course_list = current_user.course_list

	return render_template("moodle/courses.html", course_list=course_list)


@moodle.route('/courses/update/', methods=['GET'])
@login_required
@moodle_login_required
def update_courses():
	moodle_api = MoodleApi(current_user.moodle_url, current_user.token)
	course_list = moodle_api.get_user_courses(current_user.moodle_id)
	for course_info in course_list:
		course = MoodleCourse.objects(moodle_id=course_info.get('moodle_id')).first()
		if not course:
			course = MoodleCourse(moodle_id=course_info.get('moodle_id')).save()
		current_user.course_list.append(course)
		# update course forums
		forum_list = moodle_api.get_course_forums(course.moodle_id)
		for forum_info in forum_list:
			forum = MoodleForum.objects(moodle_id=forum_info.get('moodle_id')).first()
			if not forum:
				forum = MoodleForum(moodle_id=forum_info.get('moodle_id'), course=course)
				course.forum_list.append(forum)
			forum.update_forum(forum_info).save()
		course.update_course(course_info).save()
	# save updated user in db
	current_user.save()

	return redirect(url_for('.show_all_courses'))


# ********** DISCUSSIONS **********
@moodle.route('/discussions/', methods=['GET'])
@moodle.route('/discussions/<int:page>/', methods=['GET'])
@login_required
@moodle_login_required
def show_all_discussions(page=1):
	print(current_user.is_authenticated)
	moodle_api = MoodleApi(current_user.moodle_url, current_user.token)
	discussion_list = current_user.filter_and_sort_discussions().paginate(
		page=page,
		per_page=DISCUSSIONS_PER_PAGE)
	for discussion in discussion_list.items:
		user_course_grade = moodle_api.get_user_course_grade(discussion.course.moodle_id, discussion.user.moodle_id)
		if user_course_grade.get('exception'):
			print(user_course_grade.get('exception'))
		else:
			discussion.user.update_course_grade(user_course_grade.get('user_grade')).save()
			discussion.course.modify(grade_max=user_course_grade.get('course_grade')) # Плохое обновлять max балл по курсу с каждым обсуждением, нужно переделать!!!

	return render_template("moodle/discussions.html", discussion_list=discussion_list)


@moodle.route('/discussions/update/', methods=['GET'])
@login_required
@moodle_login_required
def update_discussions():
	moodle_api = MoodleApi(current_user.moodle_url, current_user.token)
	# update all discussions
	for course in current_user.course_list:
		for forum in course.forum_list:
			discussion_list = moodle_api.get_forum_discussions(forum.moodle_id)
			for discussion_info in discussion_list:
				discussion = MoodleDiscussion.objects(moodle_id=discussion_info.get('moodle_id')).first()
				if not discussion:
					discussion = MoodleDiscussion(
						moodle_id=discussion_info.get('moodle_id'),
						discussion_id=discussion_info.get('discussion_id'),
						course=course,
						forum=forum)
					forum.discussion_list.append(discussion)
				discussion.update_discussion(discussion_info).save()
			forum.save()

	return redirect(url_for('.show_all_discussions'))
