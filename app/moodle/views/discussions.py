from flask import render_template, request, redirect, url_for, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.main import main
from app.moodle import moodle
from app.moodle.views.main import moodle_login_required
from app.moodle.moodle_api import MoodleApi
from app.moodle.models import MoodleTeacher, MoodleCourse, MoodleForum, MoodleDiscussion, MoodlePost, MoodleTag, FiltrationSet

DISCUSSIONS_PER_PAGE = 5

ORDER_PARAMS = [
	{'value': '', 'label': 'По возрастанию'},
	{'value': '-', 'label': 'По убыванию'}]

@moodle.route('/discussions/', methods=['GET'])
@moodle.route('/discussions/<int:page>/', methods=['GET'])
@login_required
@moodle_login_required
def show_all_discussions(page=1):
	if request.args:
		filtration_set_info = current_user.filtration_set.parse_url_args(request.args)
		current_user.filtration_set.update_filtration_set(filtration_set_info).save()
	else:
		return redirect('{}{}'.format(url_for('.show_all_discussions', page=page), current_user.filtration_set.get_url()))
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
			discussion.course.modify(grade_max=user_course_grade.get('course_grade')) # Плохо обновлять max балл по курсу с каждым обсуждением, нужно переделать!!!

	return render_template(
		"moodle/discussions.html",
		discussion_list=discussion_list,
		tag_list=MoodleTag.objects(),
		order_select_list=ORDER_PARAMS,
		filtration_set_list=FiltrationSet.objects(),
		redirect='moodle.show_all_discussions')


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
				discussion = MoodleDiscussion.objects(moodle_id=discussion_info.get('moodle_id')).modify(
					moodle_id=discussion_info.get('moodle_id'),
					discussion_id=discussion_info.get('discussion_id'),
					course=course,
					forum=forum,
					upsert=True,
					new=True)
				# update discussion posts
				post_list = moodle_api.get_discussion_posts(discussion.discussion_id)
				for post_info in post_list:
					post = MoodlePost.objects(moodle_id=post_info.get('moodle_id')).modify(
						moodle_id=post_info.get('moodle_id'),
						course=course,
						forum=forum,
						discussion=discussion,
						upsert=True,
						new=True)
					post.update_post(post_info).save()
					discussion.post_list.append(post)
				discussion.update_discussion(discussion_info).save()
				forum.discussion_list.append(discussion)
			forum.save()

	return jsonify(redirect_url='{}{}'.format(url_for('.show_all_discussions'), current_user.filtration_set.get_url()))
