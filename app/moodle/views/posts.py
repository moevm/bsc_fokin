import time
from flask import render_template, request, redirect, url_for, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.main import main
from app.moodle import moodle
from app.moodle.views.main import moodle_login_required
from app.moodle.moodle_api import MoodleApi
from app.moodle.models import MoodlePost, MoodleTag, FiltrationSet

POSTS_PER_PAGE = 5

ORDER_PARAMS = [
	{'value': '+', 'label': 'По возрастанию'},
	{'value': '-', 'label': 'По убыванию'}]

POST_STATUSES = {
	'new': {'label': 'Новое', 'color': 'info'},
	'in progress': {'label': 'В обработке', 'color': 'secondary'},
	'closed': {'label': 'Закрыто', 'color': 'success'}}


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

	start_time = time.time()
	# start
	post_list = current_user.filter_and_sort_posts(current_user).paginate(page=page, per_page=POSTS_PER_PAGE)
	# end
	print('Поиск занял --- {} --- секунд.'.format((time.time() - start_time)))
	print('Найдено постов: {} из {}.'.format(post_list.total, MoodlePost.objects().count()))

	return render_template(
		"moodle/posts.html",
		post_list=post_list,
		tag_list=MoodleTag.objects(),
		order_select_list=ORDER_PARAMS,
		filtration_set_list=FiltrationSet.objects(),
		post_status_dict=POST_STATUSES,
		redirect_url='moodle.show_all_posts')


@moodle.route('/post/update_status/<int:post_id>/', methods=['POST'])
@login_required
@moodle_login_required
def update_post_status(post_id):
	redirect_url = request.args.get('redirect_url')
	status_info = request.get_json()
	post = MoodlePost.objects(moodle_id=post_id).first()
	post.update_post_status(status_info).save()

	return jsonify(redirect_url=redirect_url)
