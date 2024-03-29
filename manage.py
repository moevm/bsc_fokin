from datetime import datetime
from dateutil.parser import parse
from flask_script import Manager
from app.create_app import app
from app.main import main as main_blueprint
from app.stepic import stepic as stepic_blueprint
from app.moodle import moodle as moodle_blueprint
from app.filtration import filtration as filtration_blueprint


app.register_blueprint(stepic_blueprint, url_prefix='/stepic')
app.register_blueprint(moodle_blueprint, url_prefix='/moodle')
app.register_blueprint(filtration_blueprint, url_prefix='/filtration')
app.register_blueprint(main_blueprint)
manager = Manager(app)


@app.template_filter('date')
def _jinja2_filter_datetime(date, format):
	if date:
		return parse(date).strftime(format)

@app.template_filter('date_from_timestamp')
def _jinja2_filter_datetime(date, format):
	if date:
		return datetime.fromtimestamp(date).strftime(format)


if __name__ == '__main__':
	manager.run()
