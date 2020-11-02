from app.create_app import db
from app.main.models import BaseTeacher

class MoodleTeacher(BaseTeacher):
	moodle_id = db.IntField(unique=True)
	token = db.StringField(default='')
	username = db.StringField(default='')
	full_name = db.StringField(default='')
	avatar_url = db.StringField(default='')

	def get_info(self):
		return self.to_json()
