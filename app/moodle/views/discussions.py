from flask import render_template, request, redirect, url_for, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.main import main
from app.moodle import moodle
from app.moodle.views.main import moodle_login_required
from app.moodle.moodle_api import MoodleApi
from app.moodle.models import MoodleTeacher, MoodleUser, MoodleCourse, MoodleForum, MoodleDiscussion, MoodlePost, MoodleTag, FiltrationSet

DISCUSSIONS_PER_PAGE = 5

ORDER_PARAMS = [
	{'value': '+', 'label': 'По возрастанию'},
	{'value': '-', 'label': 'По убыванию'}]

POST_STATUSES = {
	'new': {'label': 'Новое', 'color': 'info'},
	'in progress': {'label': 'В обработке', 'color': 'secondary'},
	'closed': {'label': 'Закрыто', 'color': 'success'}}


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
	discussion_list = current_user.filter_and_sort_discussions(current_user).paginate(page=page, per_page=DISCUSSIONS_PER_PAGE)

	return render_template(
		"moodle/discussions.html",
		discussion_list=discussion_list,
		tag_list=MoodleTag.objects(),
		order_select_list=ORDER_PARAMS,
		filtration_set_list=FiltrationSet.objects(),
		post_status_dict=POST_STATUSES,
		redirect_url='moodle.show_all_discussions')


@moodle.route('/discussion/<int:discussion_id>/<int:post_id>/', methods=['GET'])
@login_required
@moodle_login_required
def show_discussion_tree(discussion_id, post_id):
	moodle_api = MoodleApi(current_user.moodle_url, current_user.token)
	discussion = MoodleDiscussion.objects(discussion_id=discussion_id).first()
	if not discussion:
		abort(404)

	return render_template(
		"moodle/discussion_tree.html",
		post_list=[discussion.discussion_post],
		target_post_id=post_id,
		post_status_dict=POST_STATUSES,
		redirect_url='moodle.show_discussion_tree')


@moodle.route('/discussions/update/', methods=['GET'])
@login_required
@moodle_login_required
def update_discussions():
	moodle_api = MoodleApi(current_user.moodle_url, current_user.token)
	# update all discussions
	for course in current_user.course_list:
		for forum in course.forum_list:
			discussion_list = moodle_api.get_forum_discussions(forum.moodle_id)
			forum_discussion_list = []
			for discussion_info in discussion_list:
				discussion = MoodleDiscussion.objects(moodle_id=discussion_info.get('moodle_id')).modify(
					moodle_id=discussion_info.get('moodle_id'),
					discussion_id=discussion_info.get('discussion_id'),
					course=course,
					forum=forum,
					upsert=True,
					new=True)
				# update discussion posts
				discussion_post_list = []
				post_list = moodle_api.get_discussion_posts(discussion.discussion_id)
				for post_info in post_list:
					post = MoodlePost.objects(moodle_id=post_info.get('moodle_id')).modify(
						moodle_id=post_info.get('moodle_id'),
						user=MoodleUser.objects(moodle_id=post_info.get('user_id')).modify(
							moodle_id=post_info.get('user_id'),
							full_name=post_info.get('user_full_name'),
							user_url=post_info.get('user_url'),
							user_picture_url=post_info.get('user_picture_url'),
							upsert=True,
							new=True),
						course=course,
						forum=forum,
						discussion=discussion,
						upsert=True,
						new=True)
					# update user course grade
					user_course_grade = moodle_api.get_user_course_grade(post.course.moodle_id, post.user.moodle_id)
					if user_course_grade.get('exception'):
						print(user_course_grade.get('exception'))
					else:
						post.user.update_course_grade(user_course_grade.get('user_grade')).save()
						post.course.modify(grade_max=user_course_grade.get('course_grade')) # Плохо обновлять max балл по курсу с каждым постом, нужно переделать!!!
					post.update_post(post_info).save()
					discussion_post_list.append(post)
				discussion.update_discussion(discussion_info).save()
				discussion.modify(post_list=discussion_post_list)
				forum_discussion_list.append(discussion)
			forum.modify(discussion_list=forum_discussion_list)

	return jsonify(redirect_url='{}{}'.format(url_for('.show_all_discussions'), current_user.filtration_set.get_url()))
