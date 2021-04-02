from datetime import date, timedelta
from flask import request, jsonify
from flask_login import login_required, current_user
from app.filtration import filtration


@filtration.route('/get_date_interval/', methods=['POST'])
@login_required
def get_date_interval():
	day_count = request.json.get('day_count')
	date_from = (date.today() - timedelta(int(day_count))).isoformat()
	date_to = (date.today() + timedelta(1)).isoformat()

	return jsonify(date_from=date_from, date_to=date_to)


@filtration.route('/search/', methods=['POST'])
@login_required
def search_by_filtration_set():
	redirect_url = request.args.get('redirect_url')
	filtration_set_info = request.get_json()
	current_user.filtration_set.update_filtration_set(filtration_set_info).save()

	return jsonify(redirect_url='{}{}'.format(redirect_url, current_user.filtration_set.get_url()))


@filtration.route('/import_set/<int:filtration_set_id>/', methods=['GET'])
@login_required
def import_filtration_set(filtration_set_id):
	redirect_url = request.args.get('redirect_url')
	current_user.filtration_set.import_filtration_set(filtration_set_id).save()

	return jsonify(redirect_url='{}{}'.format(redirect_url, current_user.filtration_set.get_url()))


@filtration.route('/export_set/', methods=['POST'])
@login_required
def export_filtration_set():
	redirect_url = request.args.get('redirect_url')
	filtration_set_info = request.get_json()
	current_user.filtration_set.update_filtration_set(filtration_set_info).save()
	current_user.filtration_set.export_filtration_set(filtration_set_info.get('title')).save()

	return jsonify(redirect_url='{}{}'.format(redirect_url, current_user.filtration_set.get_url()))
