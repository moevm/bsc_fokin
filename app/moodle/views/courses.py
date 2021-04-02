from flask import render_template, request, redirect, url_for, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.moodle import moodle
from app.moodle.views.main import moodle_login_required
from app.moodle.moodle_api import MoodleApi
from app.moodle.models import MoodleTeacher, MoodleCourse, MoodleForum


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
	user_course_list = []
	for course_info in course_list:
		course = MoodleCourse.objects(moodle_id=course_info.get('moodle_id')).modify(
			moodle_id=course_info.get('moodle_id'),
			upsert=True,
			new=True)
		user_course_list.append(course)
		# update course forums
		course_forum_list = []
		forum_list = moodle_api.get_course_forums(course.moodle_id)
		for forum_info in forum_list:
			forum = MoodleForum.objects(moodle_id=forum_info.get('moodle_id')).modify(
				moodle_id=forum_info.get('moodle_id'),
				course=course,
				upsert=True,
				new=True)
			forum.update_forum(forum_info).save()
			course_forum_list.append(forum)
		course.update_course(course_info).save()
		course.modify(
			forum_list=course_forum_list,
			forum_count=len(course_forum_list))
	# save updated user in db
	current_user.modify(course_list=user_course_list)

	return jsonify(redirect_url=url_for('.show_all_courses'))
