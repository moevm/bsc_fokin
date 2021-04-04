import time
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.stepic import stepic
from app.stepic.stepic_api import StepicApi
from app.stepic.models import StepicUser, StepicComment, StepicFiltrationSet
from app.stepic.views.main import stepic_login_required

COMMENTS_PER_PAGE = 5

ORDER_PARAMS = [
	{'value': '+', 'label': 'По возрастанию'},
	{'value': '-', 'label': 'По убыванию'}]

COMMENT_STATUSES = {
	'new': {'label': 'Новое', 'color': 'info'},
	'in progress': {'label': 'В обработке', 'color': 'secondary'},
	'closed': {'label': 'Закрыто', 'color': 'success'}}


@stepic.route('/comments/', methods=['GET'])
@stepic.route('/comments/<int:page>/', methods=['GET'])
@login_required
@stepic_login_required
def show_all_comments(page=1):
	if request.args:
		filtration_set_info = current_user.filtration_set.parse_url_args(request.args)
		current_user.filtration_set.update_filtration_set(filtration_set_info).save()
	else:
		return redirect('{}{}'.format(url_for('.show_all_comments', page=page), current_user.filtration_set.get_url()))

	comment_list = current_user.filter_and_sort_comments().paginate(page=page, per_page=COMMENTS_PER_PAGE)

	return render_template(
		"stepic/comments.html",
		comment_list=comment_list,
		order_select_list=ORDER_PARAMS,
		filtration_set_list=StepicFiltrationSet.objects(),
		comment_status_dict=COMMENT_STATUSES,
		redirect_url='stepic.show_all_comments')


@stepic.route('/comments/update/', methods=['GET'])
@login_required
@stepic_login_required
def update_comments():
	stepic_api = StepicApi(current_user.token)
	# update all comments
	old_comment_amount = StepicComment.objects().count()
	start_time = time.time()
	# start
	for course in current_user.course_list:
		comment_list = stepic_api.get_course_comments(course.stepic_id)
		for comment_info in comment_list:
			comment = StepicComment.objects(stepic_id=comment_info.get('stepic_id')).modify(
				stepic_id=comment_info.get('stepic_id'),
				user=StepicUser.objects(stepic_id=comment_info.get('user_id')).modify(
					stepic_id=comment_info.get('user_id'),
					upsert=True,
					new=True),
				course=course,
				upsert=True,
				new=True)
			# add comment step_id in user course steps dict
			comment.user.add_step(comment_info).save()
			# update comment info
			comment.update_comment(comment_info).save()
	# update all users
	user_id_list = StepicUser.objects().distinct('stepic_id')
	user_list = stepic_api.get_users_info(user_id_list)
	for user_info in user_list:
		StepicUser.objects(stepic_id=user_info['id']).first().update_user(user_info).save()

	# end
	print('Импорт данных занял --- {} --- секунд.'.format((time.time() - start_time)))
	print('Загружено комментариев: {}, новых: {}.'.format(StepicComment.objects().count(), (StepicComment.objects().count() - old_comment_amount)))

	return jsonify(redirect_url='{}{}'.format(url_for('.show_all_comments'), current_user.filtration_set.get_url()))


@stepic.route('/comment/update_status/<int:comment_id>/', methods=['POST'])
@login_required
@stepic_login_required
def update_comment_status(comment_id):
	redirect_url = request.args.get('redirect_url')
	status_info = request.get_json()
	comment = MoodlePost.objects(stepic_id=comment_id).first()
	comment.update_comment_status(status_info).save()

	return jsonify(redirect_url=redirect_url)


@stepic.route('/stepic_comment/<int:step_id>/<int:comment_id>/', methods=['GET'])
@login_required
@stepic_login_required
def show_comment(step_id, comment_id):
	stepic_api = StepicApi(session['token'])
	step_info = stepic_api.get_step_info(step_id)
	comment_url = 'https://stepik.org/lesson/{}/step/{}?discussion={}'.format(step_info['lesson'], step_info['position'], comment_id)

	return redirect(comment_url)
