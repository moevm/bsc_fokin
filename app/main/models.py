from flask_login import UserMixin
from app.create_app import db, login_manager

class BaseTeacher(UserMixin, db.Document):
	serial_id = db.SequenceField()
	meta = {'allow_inheritance': True}

	def get_info(self):
		return self.to_json()

	def is_stepic_teacher(self):
		return True if self._cls == 'BaseTeacher.StepicTeacher' else False

	def is_moodle_teacher(self):
		return True if self._cls == 'BaseTeacher.MoodleTeacher' else False


@login_manager.user_loader
def load_user(user_id):
	try:
		return BaseTeacher.objects(id=user_id).first()
	except:
		return None
