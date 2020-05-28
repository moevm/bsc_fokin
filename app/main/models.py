from app.create_app import db, login_manager
from flask_login import UserMixin
from app.main.stepic import StepicApi


class Filter(db.EmbeddedDocument):
	sort = db.StringField(default='')
	order = db.StringField(default='')

class Teacher(UserMixin, db.Document):
	serial_id = db.SequenceField()
	stepic_id = db.IntField(unique=True)
	full_name = db.StringField(default='')
	avatar_url = db.StringField(default='')
	course_list = db.ListField(default=[])
	filter_list = db.ListField(db.EmbeddedDocumentField(Filter),
							   default=[Filter(sort='reply_count', order = ''),
										Filter(sort='epic_count', order = '-'),
										Filter(sort='user_reputation', order = '-'),
										Filter(sort='abuse_count', order = ''),
										Filter(sort='time', order = '-')])

	def get_id(self):
		return str(self.id)

	def get_info(self):
		return self.to_json()

	def update_filters(self, form):
		for i in range(5):
			self.filter_list[i] = Filter(sort=form.get('sorting_{}'.format(i + 1)), order=form.get('ordering_{}'.format(i + 1)))

		return self

	def get_filters(self):
		return list(map(lambda x: '{}{}'.format(x.order, x.sort), self.filter_list))


class Course(db.Document):
	serial_id = db.SequenceField()
	stepic_id = db.IntField(unique=True)
	title = db.StringField(default='')
	summary = db.StringField(default='')
	cover = db.StringField(default='')
	cert_reg_threshold = db.IntField(default=0)
	cert_dist_threshold = db.IntField(default=0)
	score = db.IntField(default=0)

	def get_info(self):
		return self.to_json()

	def update_course(self, course_info):
		self.stepic_id=course_info['stepic_id']
		self.title=course_info['title']
		self.summary=course_info['summary']
		self.cover=course_info['cover']
		self.cert_reg_threshold=course_info['cert_reg_threshold']
		self.cert_dist_threshold=course_info['cert_dist_threshold']
		self.score=course_info['score']

		return self


class UserStep(db.EmbeddedDocument):
	score = db.IntField(default=0)
	is_passed = db.BooleanField(default=False)
	is_passed_on_comment = db.BooleanField(default=False)
	total_submissions = db.IntField(default=0)
	submissions_on_comment = db.IntField(default=0)

	def get_info(self):
		return self.to_json()

	def update_user_step(self, step_grades):
		self.score=step_grades['score']
		self.is_passed=step_grades['is_passed']
		self.total_submissions=step_grades['total_submissions']

		return self


class UserCourse(db.EmbeddedDocument):
	score = db.IntField(default=0)
	steps = db.MapField(db.EmbeddedDocumentField(UserStep))

	def get_info(self):
		return self.to_json()

	def add_step(self, comment_info):
		user_step = self.steps.get(str(comment_info['step_id']))
		if not user_step:
			self.steps[str(comment_info['step_id'])]=UserStep()

		return self

	def update_step_grades(self, course_grades):
		self.score=course_grades['score']
		for step_id in self.steps:
			for step_grades in course_grades['results']:
				if str(course_grades['results'][step_grades]['step_id']) == step_id:
					self.steps[step_id].update_user_step(course_grades['results'][step_grades])
					break

		return self


class User(db.Document):
	serial_id = db.SequenceField()
	stepic_id = db.IntField(unique=True)
	full_name = db.StringField(default='')
	avatar_url = db.StringField(default='')
	reputation = db.IntField(default=0)
	courses = db.MapField(db.EmbeddedDocumentField(UserCourse))

	def get_info(self):
		return self.to_json()

	def update_user(self, user_info):
		self.full_name=user_info['full_name']
		self.avatar_url=user_info['avatar']
		self.reputation=user_info['reputation']

		return self

	def add_step(self, comment_info):
		user_course = self.courses.get(str(comment_info['course_id']))
		if user_course:
			user_course.add_step(comment_info)
		else:
			self.courses[str(comment_info['course_id'])]=UserCourse().add_step(comment_info)

		return self

	def update_course_grades(self, token):
		stepic_api = StepicApi(token)
		for course_id in self.courses:
			course_grades = stepic_api.get_user_course_grades(course_id, self.stepic_id)
			if course_grades:
				self.courses[course_id].update_step_grades(course_grades[0])

		return self


class Comment(db.Document):
	serial_id = db.SequenceField()
	stepic_id = db.IntField(unique=True)
	parent_id = db.IntField()
	step_id = db.IntField()
	user = db.ReferenceField(User)
	user_reputation = db.IntField(default=0)
	course = db.ReferenceField(Course)
	user_role = db.StringField(default='')
	time = db.StringField(default='')
	last_time = db.StringField(default='')
	text = db.StringField(default='')
	# replies = db.ListField(db.ReferenceField('self'))
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

	def update_comment(self, comment_info):
		self.stepic_id=comment_info['stepic_id']
		self.parent_id=comment_info['parent_id']
		self.step_id=comment_info['step_id']
		self.user_role=comment_info['user_role']
		self.time=comment_info['time']
		self.last_time=comment_info['last_time']
		self.text=comment_info['text']
		# self.replies=comment_info['replies']
		self.reply_count=comment_info['reply_count']
		self.is_deleted=comment_info['is_deleted']
		self.is_pinned=comment_info['is_pinned']
		self.is_staff_replied=comment_info['is_staff_replied']
		self.is_reported=comment_info['is_reported']
		self.attachments=comment_info['attachments']
		self.epic_count=comment_info['epic_count']
		self.abuse_count=comment_info['abuse_count']

		return self


@login_manager.user_loader
def load_user(user_id):
	try:
		return Teacher.objects(id=user_id).first()
	except:
		return None
