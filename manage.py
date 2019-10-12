from flask_script import Manager
from app.create_app import app
from app.main import main as main_blueprint
from app.main.models import Teacher
from dateutil.parser import parse


app.register_blueprint(main_blueprint)
manager = Manager(app)


@app.template_filter('date')
def _jinja2_filter_datetime(date, format):
    if date :
        return parse(date).strftime(format)


@manager.option('-stepic_id')
def new_teacher(stepic_id):
	try:
		teacher = Teacher(stepic_id=stepic_id, full_name='', avatar_url='')
		teacher.save()
		print("Base teacher added")
	except Exception as e:
		print(e)


if __name__ == '__main__':
	manager.run()
