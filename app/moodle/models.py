from app.create_app import db
from app.main.models import BaseTeacher


class MoodleTag(db.Document):
	serial_id = db.SequenceField()
	moodle_id = db.IntField(unique=True)
	# TODO: other fields and methods

	def get_info(self):
		return self.to_json()


class MoodlePost(db.Document):
	serial_id = db.SequenceField()
	moodle_id = db.IntField(unique=True)
	subject = db.StringField(default='')
	reply_subject = db.StringField(default='')
	message = db.StringField(default='')
	author_id = db.IntField(default=0) # ? ReferenceField
	author_fullname = db.StringField(default='')
	author_profile_url = db.StringField(default='')
	author_profile_image_url = db.StringField(default='')
	has_parent = db.BooleanField(default=False)
	parent_id = db.IntField(default=0) # ? ReferenceField
	time_created = db.IntField(default=0)
	tag_list = db.ListField(db.ReferenceField(MoodleTag), default=[])

	def get_info(self):
		return self.to_json()

	def update_post(self, post_info):
		# TODO:

		return self


class MoodleDiscussion(db.Document):
	serial_id = db.SequenceField()
	moodle_id = db.IntField(unique=True)
	discussion_id = db.IntField(unique=True)
	course = db.ReferenceField('MoodleCourse')
	forum = db.ReferenceField('MoodleForum')
	name = db.StringField(default='')
	subject = db.StringField(default='')
	message = db.StringField(default='')
	created = db.IntField(default=0)
	user = db.ReferenceField('MoodleUser')
	time_modified = db.IntField(default=0)
	user_modified = db.IntField(default=0) # ? ReferenceField
	num_replies = db.IntField(default=0)
	post_list = db.ListField(db.ReferenceField(MoodlePost), default=[])

	def get_info(self):
		return self.to_json()

	def update_discussion(self, discussion_info):
		self.name = discussion_info.get('name')
		self.subject = discussion_info.get('subject')
		self.message = discussion_info.get('message')
		self.created = discussion_info.get('created')
		self.time_modified = discussion_info.get('time_modified')
		self.user_modified = discussion_info.get('user_modified')
		self.num_replies = discussion_info.get('num_replies')
		self.user = MoodleUser.objects(moodle_id=discussion_info.get('user_id')).modify(
			full_name=discussion_info.get('user_full_name'),
			user_picture_url=discussion_info.get('user_picture_url'),
			upsert=True,
			new=True)

		return self


class MoodleForum(db.Document):
	serial_id = db.SequenceField()
	moodle_id = db.IntField(unique=True)
	course = db.ReferenceField('MoodleCourse')
	type = db.StringField(default='')
	name = db.StringField(default='')
	intro = db.StringField(default='')
	scale = db.IntField(default=0)
	discussion_list = db.ListField(db.ReferenceField(MoodleDiscussion), default=[])

	def get_info(self):
		return self.to_json()

	def update_forum(self, forum_info):
		self.type = forum_info.get('type')
		self.name = forum_info.get('name')
		self.intro = forum_info.get('intro')
		self.scale = forum_info.get('scale')

		return self


class MoodleCourse(db.Document):
	serial_id = db.SequenceField()
	moodle_id = db.IntField(unique=True)
	short_name = db.StringField(default='')
	full_name = db.StringField(default='')
	display_name = db.StringField(default='')
	summary = db.StringField(default='')
	enrolled_user_count = db.IntField(default=0)
	visible = db.BooleanField(default=False)
	format = db.StringField(default='')
	grade_max = db.IntField(default=0)
	show_grades = db.BooleanField(default=False)
	start_date = db.IntField(default=0)
	cover = db.StringField(default='')
	forum_list = db.ListField(db.ReferenceField(MoodleForum), default=[])
	forum_count = db.IntField(default=0)

	def get_info(self):
		return self.to_json()

	def update_course(self, course_info):
		self.short_name = course_info.get('short_name')
		self.full_name = course_info.get('full_name')
		self.display_name = course_info.get('display_name')
		self.summary = course_info.get('summary')
		self.enrolled_user_count = course_info.get('enrolled_user_count')
		self.visible = course_info.get('visible')
		self.format = course_info.get('format')
		self.show_grades = course_info.get('show_grades')
		self.start_date = course_info.get('start_date')
		self.cover = course_info.get('cover')
		self.forum_count = len(self.forum_list)

		return self


class MoodleUser(db.Document):
	moodle_id = db.IntField()
	full_name = db.StringField(default='')
	user_picture_url = db.StringField(default='')
	course_grade_dict= db.DictField(default={})

	def get_info(self):
		return self.to_json()

	def update_course_grade(self, user_course_grade):
		self.course_grade_dict.update(user_course_grade)

		return self


class MoodleTeacher(BaseTeacher):
	moodle_url = db.StringField(default='')
	moodle_id = db.IntField()
	token = db.StringField(default='')
	username = db.StringField(default='')
	full_name = db.StringField(default='')
	user_picture_url = db.StringField(default='')
	course_list = db.ListField(db.ReferenceField(MoodleCourse), default=[])

	def get_info(self):
		return self.to_json()

	def filter_and_sort_discussions(self):
		# filter
		# 1. course
		discussions_list = MoodleDiscussion.objects(course__in=self.course_list)

		return discussions_list
