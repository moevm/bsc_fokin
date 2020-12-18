from app.create_app import db
from app.main.models import BaseTeacher


class FiltrationSet(db.Document):
	serial_id = db.SequenceField()
	title = db.StringField(default='', unique=True)
	date_from = db.StringField(default='')
	date_to = db.StringField(default='')
	date_order = db.StringField(default='-')
	replies_from = db.IntField(default=0)
	replies_to = db.IntField(default=10)
	replies_order = db.StringField(default='-')
	progress_from = db.IntField(default=50)
	progress_to = db.IntField(default=80)
	progress_order = db.StringField(default='-')
	course_id_list = db.ListField(default=[])
	tag_id_list = db.ListField(default=[])

	def get_info(self):
		return self.to_json()

	def update_filtration_set(self, filtration_set_info):
		self.date_from = filtration_set_info.get('date[from]')
		self.date_to = filtration_set_info.get('date[to]')
		self.date_order = filtration_set_info.get('date[order]')
		self.replies_from = filtration_set_info.get('replies[from]')
		self.replies_to = filtration_set_info.get('replies[to]')
		self.replies_order = filtration_set_info.get('replies[order]')
		self.progress_from = filtration_set_info.get('progress[from]')
		self.progress_to = filtration_set_info.get('progress[to]')
		self.progress_order = filtration_set_info.get('progress[order]')
		self.course_id_list = list(map(int, filtration_set_info.getlist('course_ids[]')))
		self.tag_id_list = list(map(int, filtration_set_info.getlist('tag_ids[]')))

		return self


class MoodleTag(db.Document):
	serial_id = db.SequenceField()
	moodle_id = db.IntField(unique=True)
	tag_id = db.IntField()
	is_standard = db.BooleanField(default=False)
	display_name = db.StringField(default='')

	def get_info(self):
		return self.to_json()


class MoodlePost(db.Document):
	serial_id = db.SequenceField()
	moodle_id = db.IntField(unique=True)
	user = db.ReferenceField('MoodleUser')
	course = db.ReferenceField('MoodleCourse')
	forum = db.ReferenceField('MoodleForum')
	discussion = db.ReferenceField('MoodleDiscussion')
	subject = db.StringField(default='')
	reply_subject = db.StringField(default='')
	message = db.StringField(default='')
	has_parent = db.BooleanField(default=False)
	parent_id = db.IntField(default=0) # ? ReferenceField
	time_created = db.IntField(default=0)
	rating = db.IntField(default=0)
	rating_count = db.IntField(default=0)
	rating_label = db.StringField(default='')
	tag_list = db.ListField(db.ReferenceField(MoodleTag), default=[])

	def get_info(self):
		return self.to_json()

	def update_post(self, post_info):
		self.user = MoodleUser.objects(moodle_id=post_info.get('user_id')).modify(
			moodle_id=post_info.get('user_id'),
			full_name=post_info.get('user_full_name'),
			user_url=post_info.get('user_url'),
			user_picture_url=post_info.get('user_picture_url'),
			upsert=True,
			new=True)
		self.subject = post_info.get('subject')
		self.reply_subject = post_info.get('reply_subject')
		self.message = post_info.get('message')
		self.has_parent = post_info.get('has_parent')
		self.parent_id = post_info.get('parent_id')
		self.time_created = post_info.get('time_created')
		if post_info.get('rating'):
			self.rating = post_info.get('rating').get('rating')
			self.rating_count = post_info.get('rating').get('count')
			self.rating_label = post_info.get('rating').get('aggregatelabel')
		self.tag_list = [
			MoodleTag.objects(moodle_id=tag_info.get('id')).modify(
				moodle_id=tag_info.get('id'),
				tag_id=tag_info.get('tagid'),
				is_standard=tag_info.get('isstandard'),
				display_name=tag_info.get('displayname'),
				upsert=True,
				new=True)
			for tag_info in post_info.get('tags')]

		return self


class MoodleDiscussion(db.Document):
	serial_id = db.SequenceField()
	moodle_id = db.IntField(unique=True)
	discussion_id = db.IntField(unique=True)
	user = db.ReferenceField('MoodleUser')
	course = db.ReferenceField('MoodleCourse')
	forum = db.ReferenceField('MoodleForum')
	name = db.StringField(default='')
	subject = db.StringField(default='')
	message = db.StringField(default='')
	created = db.IntField(default=0)
	time_modified = db.IntField(default=0)
	user_modified = db.IntField(default=0) # ? ReferenceField
	num_replies = db.IntField(default=0)
	post_list = db.ListField(db.ReferenceField(MoodlePost), default=[])

	def get_info(self):
		return self.to_json()

	def update_discussion(self, discussion_info):
		self.user = MoodleUser.objects(moodle_id=discussion_info.get('user_id')).modify(
			full_name=discussion_info.get('user_full_name'),
			user_picture_url=discussion_info.get('user_picture_url'),
			upsert=True,
			new=True)
		self.name = discussion_info.get('name')
		self.subject = discussion_info.get('subject')
		self.message = discussion_info.get('message')
		self.created = discussion_info.get('created')
		self.time_modified = discussion_info.get('time_modified')
		self.user_modified = discussion_info.get('user_modified')
		self.num_replies = discussion_info.get('num_replies')

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
	user_url = db.StringField(default='')
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
	filtration_set = db.ReferenceField(FiltrationSet)

	def get_info(self):
		return self.to_json()

	def update_teacher(self, teacher_info):
		self.username = teacher_info.get('username')
		self.full_name = teacher_info.get('fullname')
		self.user_picture_url = teacher_info.get('userpictureurl')
		filtration_set_title = '{} (по умолчанию)'.format(teacher_info.get('username'))
		self.filtration_set = FiltrationSet.objects(title=filtration_set_title).modify(
				title=filtration_set_title,
				upsert=True,
				new=True)

		return self

	def filter_and_sort_discussions(self):
		# filter
		# 1. course
		discussions_list = MoodleDiscussion.objects(course__in=self.course_list)

		return discussions_list
