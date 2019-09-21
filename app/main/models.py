from app.create_app import db, login_manager
from flask_login import UserMixin


class Teacher(UserMixin, db.Document):
	_id = db.ObjectIdField()
	serial_id = db.SequenceField()
	stepic_id = db.IntField(unique=True)
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
	stepic_id = db.IntField(unique=True)
	title = db.StringField(default='')
	summary = db.StringField(default='')
	cover = db.StringField(default='')
	cert_reg_threshold = db.IntField(default=0)
	cert_dist_threshold = db.IntField(default=0)
	score = db.IntField(default=0)
	steps = db.ListField(default=[])
	is_selected = db.BooleanField(default=False)

	def get_info(self):
		return self.to_json()


class Comment(db.Document):
	_id = db.ObjectIdField()
	serial_id = db.SequenceField()
	stepic_id = db.IntField(unique=True)
	parent_id = db.IntField()
	step_id = db.IntField()
	user_id = db.IntField()
	user_role = db.StringField(default='')
	time = db.StringField(default='')
	last_time = db.StringField(default='')
	text = db.StringField(default='')
	replies = db.ListField(default=[])
	reply_count = db.IntField(default=0)
	is_deleted = db.BooleanField(default=False)
	is_pinned = db.BooleanField(default=False)
	is_staff_replied = db.BooleanField(default=False)
	is_reported = db.BooleanField(default=False)
	attachments = db.ListField(default=[])
	epic_count = db.IntField(default=0)
	abuse_count = db.IntField(default=0)

	def get_info(self):
		return self.to_json()


@login_manager.user_loader
def load_user(user_id):
	try:
		return Teacher.objects(_id=user_id).first()
	except:
		return None
