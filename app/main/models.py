from app.create_app import db, login_manager
from flask_login import UserMixin


class Teacher(UserMixin, db.Document):
	_id = db.ObjectIdField()
	serial_id = db.SequenceField()
	stepic_id = db.StringField(unique=True)
	full_name = db.StringField(default='')
	avatar_url = db.StringField(default='')
	course_list = db.ListField(default=[])

	def get_id(self):
		return str(self._id)

	def get_info(self):
		return self.to_json()


class Course(db.Document):
	_id = db.ObjectIdField()
	serial_id = db.SequenceField()
	stepic_id = db.StringField(unique=True)
	title = db.StringField(default='')
	summary = db.StringField(default='')
	cover = db.StringField(default='')
	cert_reg_threshold = db.IntField(default=0)
	cert_dist_threshold = db.IntField(default=0)
	score = db.IntField(default=0)
	steps = db.ListField(default=[])


@login_manager.user_loader
def load_user(user_id):
	try:
		return Teacher.objects(_id=user_id).first()
	except:
		return None
