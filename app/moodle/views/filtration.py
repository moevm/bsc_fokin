from flask import render_template, request, redirect, url_for, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.moodle import moodle
from app.moodle.views.main import moodle_login_required
from app.moodle.models import FiltrationSet


@moodle.route('/filtration_set/import/<int:filtration_set_id>/', methods=['GET'])
@login_required
@moodle_login_required
def import_filtration_set(filtration_set_id):
	redirect_url = request.args.get('redirect_url')
	old_filtration_set = FiltrationSet.objects(serial_id=filtration_set_id).first()
	current_user.filtration_set.copy_filtration_set(old_filtration_set).save()

	return jsonify(redirect_url='{}{}'.format(redirect_url, current_user.filtration_set.get_url()))


@moodle.route('/filtration_set/export/', methods=['POST'])
@login_required
@moodle_login_required
def export_filtration_set():
	redirect_url = request.args.get('redirect_url')
	filtration_set_info = request.get_json()
	new_filtration_set = FiltrationSet(title=filtration_set_info.get('title')).update_filtration_set(filtration_set_info).save()
	current_user.filtration_set.update_filtration_set(filtration_set_info).save()

	return jsonify(redirect_url='{}{}'.format(redirect_url, current_user.filtration_set.get_url()))


@moodle.route('/filtration_set/search/', methods=['POST'])
@login_required
@moodle_login_required
def search_by_filtration_set():
	redirect_url = request.args.get('redirect_url')
	filtration_set_info = request.get_json()
	current_user.filtration_set.update_filtration_set(filtration_set_info).save()

	return jsonify(redirect_url='{}{}'.format(redirect_url, current_user.filtration_set.get_url()))
