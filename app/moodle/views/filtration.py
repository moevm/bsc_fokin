from flask import render_template, request, redirect, url_for, abort
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from app.main import main
from app.moodle import moodle
from app.moodle.views.main import moodle_login_required
from app.moodle.models import FiltrationSet


@moodle.route('/filtration_set/import/<int:filtration_set_id>/', methods=['GET'])
@login_required
@moodle_login_required
def import_filtration_set(filtration_set_id):
	redirect_url = request.args.get('redirect')
	filtration_set = FiltrationSet.objects(serial_id=filtration_set_id).first()
	print(filtration_set.to_json(), filtration_set.get_url())

	return redirect('{}{}'.format(url_for('.{}'.format(redirect_url), page=1), filtration_set.get_url()))


@moodle.route('/filtration_set/export/', methods=['GET'])
@login_required
@moodle_login_required
def export_filtration_set():
	redirect_url = request.args.get('redirect')
	filtration_set_info = request.args
	current_user.filtration_set = FiltrationSet(title=filtration_set_info.get('title')).update_filtration_set(filtration_set_info).save()

	return redirect('{}{}'.format(url_for('.{}'.format(redirect_url), page=1), current_user.filtration_set.get_url()))
