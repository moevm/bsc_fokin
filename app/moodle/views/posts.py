from flask import render_template, request, redirect, url_for, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.main import main
from app.moodle import moodle
from app.moodle.views.main import moodle_login_required
from app.moodle.moodle_api import MoodleApi
from app.moodle.models import MoodlePost, MoodleTag, FiltrationSet

POSTS_PER_PAGE = 5

ORDER_PARAMS = [
	{'value': '', 'label': 'По возрастанию'},
	{'value': '-', 'label': 'По убыванию'}]


@moodle.route('/posts/', methods=['GET'])
@moodle.route('/posts/<int:page>/', methods=['GET'])
@login_required
@moodle_login_required
def show_all_posts(page=1):
	if request.args:
		filtration_set_info = current_user.filtration_set.parse_url_args(request.args)
		current_user.filtration_set.update_filtration_set(filtration_set_info).save()
	else:
		return redirect('{}{}'.format(url_for('.show_all_posts', page=page), current_user.filtration_set.get_url()))
	moodle_api = MoodleApi(current_user.moodle_url, current_user.token)
	post_list = current_user.filter_and_sort_posts().paginate(
		page=page,
		per_page=POSTS_PER_PAGE)
	for post in post_list.items:
		user_course_grade = moodle_api.get_user_course_grade(post.course.moodle_id, post.user.moodle_id)
		if user_course_grade.get('exception'):
			print(user_course_grade.get('exception'))
		else:
			post.user.update_course_grade(user_course_grade.get('user_grade')).save()
			post.course.modify(grade_max=user_course_grade.get('course_grade')) # Плохо обновлять max балл по курсу с каждым обсуждением, нужно переделать!!!

	return render_template(
		"moodle/posts.html",
		post_list=post_list,
		tag_list=MoodleTag.objects(),
		order_select_list=ORDER_PARAMS,
		filtration_set_list=FiltrationSet.objects(),
		redirect='moodle.show_all_posts')
