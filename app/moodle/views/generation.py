import math
import random
from flask import render_template, request, redirect, url_for, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.main import main
from app.moodle import moodle
from app.moodle.views.main import moodle_login_required
from app.moodle.moodle_api import MoodleApi
from app.moodle.models import MoodleCourse, MoodleForum


GEN_AMOUNTS = [10, 50, 100]
POSTS_PER_DISCUSSION = 5
COURSE_IDS = []
USER_TOKENS = []


@moodle.route('/generator/', methods=['GET'])
@login_required
@moodle_login_required
def show_moodle_gen_page():

	return render_template("moodle/gen_moodle_data.html", amount_select_list=GEN_AMOUNTS)


@moodle.route('/generate/', methods=['POST'])
@login_required
@moodle_login_required
def generate_moodle_data():
	post_amount = int(request.get_json().get('amount'))
	discussion_amount = math.ceil(post_amount // POSTS_PER_DISCUSSION)
	course_list = MoodleCourse.objects(moodle_id__in=COURSE_IDS)
	forum_list = MoodleForum.objects(course__in=course_list)
	forum_id_list = [forum.moodle_id for forum in forum_list if (forum.type == 'blog' or forum.type == 'general')]
	moodle_api_list = [MoodleApi(current_user.moodle_url, token) for token in USER_TOKENS]

	for i in range(discussion_amount):
		forum_id = random.choice(forum_id_list)
		discussion_id = random.choice(moodle_api_list).add_forum_discussion(forum_id)
		discussion_post_amount = POSTS_PER_DISCUSSION if post_amount > POSTS_PER_DISCUSSION else post_amount
		for j in range(discussion_post_amount):
			post_id = random.choice(moodle_api_list).add_discussion_post(discussion_id)
			post_amount -= 1

	return jsonify(redirect_url=url_for('.show_moodle_gen_page'))
