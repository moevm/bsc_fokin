import time
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.stepic import stepic
from app.stepic.stepic_api import StepicApi
from app.stepic.models import StepicUser, StepicReview, StepicFiltrationSet
from app.stepic.views.main import stepic_login_required

REVIEWS_PER_PAGE = 5

ORDER_PARAMS = [
	{'value': '+', 'label': 'По возрастанию'},
	{'value': '-', 'label': 'По убыванию'}]


@stepic.route('/reviews/', methods=['GET'])
@stepic.route('/reviews/<int:page>/', methods=['GET'])
@login_required
@stepic_login_required
def show_all_reviews(page=1):
	if request.args:
		filtration_set_info = current_user.filtration_set.parse_url_args(request.args)
		current_user.filtration_set.update_filtration_set(filtration_set_info).save()
	else:
		return redirect('{}{}'.format(url_for('.show_all_reviews', page=page), current_user.filtration_set.get_url()))

	review_list = current_user.filter_and_sort_reviews().paginate(page=page, per_page=REVIEWS_PER_PAGE)

	return render_template(
		"stepic/reviews.html",
		review_list=review_list,
		order_select_list=ORDER_PARAMS,
		filtration_set_list=StepicFiltrationSet.objects(),
		redirect_url='stepic.show_all_reviews')


@stepic.route('/reviews/update/', methods=['GET'])
@login_required
@stepic_login_required
def update_reviews():
	stepic_api = StepicApi(current_user.token)
	# update all reviews
	old_review_amount = StepicReview.objects().count()
	start_time = time.time()
	# start
	for course in current_user.course_list:
		review_list = stepic_api.get_course_reviews(course.stepic_id)
		for review_info in review_list:
			review = StepicReview.objects(stepic_id=review_info.get('stepic_id')).modify(
				stepic_id=review_info.get('stepic_id'),
				user=StepicUser.objects(stepic_id=review_info.get('user_id')).modify(
					stepic_id=review_info.get('user_id'),
					upsert=True,
					new=True),
				course=course,
				upsert=True,
				new=True)
			# add review course_id in user course steps dict
			review.user.add_course(review_info).save()
			# update comment info
			review.update_review(review_info).save()
	# update all users
	user_id_list = StepicUser.objects().distinct('stepic_id')
	user_list = stepic_api.get_users_info(user_id_list)
	for user_info in user_list:
		StepicUser.objects(stepic_id=user_info['id']).first().update_user(user_info).save()

	# end
	print('Импорт данных занял --- {} --- секунд.'.format((time.time() - start_time)))
	print('Загружено отзывов: {}, новых: {}.'.format(StepicReview.objects().count(), (StepicReview.objects().count() - old_review_amount)))

	return jsonify(redirect_url='{}{}'.format(url_for('.show_all_reviews'), current_user.filtration_set.get_url()))


@stepic.route('/stepic_review/<int:review_id>/', methods=['GET'])
@login_required
@stepic_login_required
def show_review(review_id):
	review = StepicReview.objects(stepic_id=review_id).first()
	review_url = 'https://stepik.org/course/{}/reviews/{}'.format(review.course.stepic_id, review.stepic_id)

	return redirect(review_url)
