from datetime import date, datetime
from app.create_app import db
from app.main.models import BaseTeacher


class FiltrationSet(db.Document):
	serial_id = db.SequenceField()
	title = db.StringField(default='', unique=True)
	date_from = db.IntField(default=0)
	date_to = db.IntField(default=0)
	date_order = db.StringField(default='-')
	replies_from = db.IntField(default=0)
	replies_to = db.IntField(default=10)
	replies_order = db.StringField(default='-')
	progress_from = db.IntField(default=50)
	progress_to = db.IntField(default=80)
	progress_order = db.StringField(default='-')
	course_id_list = db.ListField(default=[])
	tag_id_list = db.ListField(default=[])
	author = db.ReferenceField('MoodleUser')
	post_status = db.StringField(default='all')

	def get_info(self):
		return self.to_json()

	def parse_url_args(self, args):
		filtration_set_info = {
			'date_from': args.get('date[from]'),
			'date_to': args.get('date[to]'),
			'date_order': args.get('date[order]'),
			'replies_from': args.get('replies[from]'),
			'replies_to': args.get('replies[to]'),
			'replies_order': args.get('replies[order]'),
			'progress_from': args.get('progress[from]'),
			'progress_to': args.get('progress[to]'),
			'progress_order': args.get('progress[order]'),
			'course_id_list': args.getlist('course_ids[]'),
			'tag_id_list': args.getlist('tag_ids[]'),
			'author_id': args.get('author_id'),
			'post_status': args.get('post_status')
		}

		return filtration_set_info

	def update_filtration_set(self, filtration_set_info):
		self.date_from = datetime.fromisoformat(filtration_set_info.get('date_from')).timestamp()
		self.date_to = datetime.fromisoformat(filtration_set_info.get('date_to')).timestamp()
		self.date_order = filtration_set_info.get('date_order')
		self.replies_from = filtration_set_info.get('replies_from')
		self.replies_to = filtration_set_info.get('replies_to')
		self.replies_order = filtration_set_info.get('replies_order')
		self.progress_from = filtration_set_info.get('progress_from')
		self.progress_to = filtration_set_info.get('progress_to')
		self.progress_order = filtration_set_info.get('progress_order')
		self.course_id_list = list(map(int, filtration_set_info.get('course_id_list'))) if filtration_set_info.get('course_id_list') else []
		self.tag_id_list = list(map(int, filtration_set_info.get('tag_id_list'))) if filtration_set_info.get('tag_id_list') else []
		self.author = MoodleUser.objects(serial_id=filtration_set_info.get('author_id')).first() if filtration_set_info.get('author_id') else None
		self.post_status = filtration_set_info.get('post_status')

		print('Update filtration set #{}'.format(self.serial_id))

		return self

	def copy_filtration_set(self, old_filtration_set):
		self.date_from = old_filtration_set.date_from
		self.date_to = old_filtration_set.date_to
		self.date_order = old_filtration_set.date_order
		self.replies_from = old_filtration_set.replies_from
		self.replies_to = old_filtration_set.replies_to
		self.replies_order = old_filtration_set.replies_order
		self.progress_from = old_filtration_set.progress_from
		self.progress_to = old_filtration_set.progress_to
		self.progress_order = old_filtration_set.progress_order
		self.course_id_list = old_filtration_set.course_id_list
		self.tag_id_list = old_filtration_set.tag_id_list
		self.author = old_filtration_set.author
		self.post_status = old_filtration_set.post_status

		print('Copy filtration_set #{} <-- #{}'.format(self.serial_id, old_filtration_set.serial_id))

		return self

	def get_url(self):
		url = '?{}&{}&{}&{}&{}&{}&{}'.format(
			self.get_date_args_url(),
			self.get_replies_args_url(),
			self.get_progress_args_url(),
			self.get_courses_args_url(),
			self.get_tags_args_url(),
			self.get_author_args_url(),
			self.get_post_status_args_url())

		return url

	def get_date_args_url(self):
		date_args_url = 'date[from]={}&date[to]={}&date[order]={}'.format(
			date.fromtimestamp(self.date_from).isoformat(),
			date.fromtimestamp(self.date_to).isoformat(),
			self.date_order)

		return date_args_url

	def get_replies_args_url(self):
		replies_args_url = 'replies[from]={}&replies[to]={}&replies[order]={}'.format(
			self.replies_from,
			self.replies_to,
			self.replies_order)

		return replies_args_url

	def get_progress_args_url(self):
		progress_args_url = 'progress[from]={}&progress[to]={}&progress[order]={}'.format(
			self.progress_from,
			self.progress_to,
			self.progress_order)

		return progress_args_url

	def get_courses_args_url(self):
		return '&'.join('course_ids[]={}'.format(course_id) for course_id in self.course_id_list)

	def get_tags_args_url(self):
		return '&'.join('tag_ids[]={}'.format(tag_id) for tag_id in self.tag_id_list)

	def get_author_args_url(self):
		return 'author_id={}'.format(self.author.serial_id if self.author else 0)

	def get_post_status_args_url(self):
		return 'post_status={}'.format(self.post_status)


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
	parent_post = db.ReferenceField('MoodlePost')
	time_created = db.IntField(default=0)
	view_url = db.StringField(default='')
	rating = db.IntField(default=0)
	rating_count = db.IntField(default=0)
	rating_label = db.StringField(default='')
	tag_list = db.ListField(db.ReferenceField('MoodleTag'), default=[])
	post_list = db.ListField(db.ReferenceField('MoodlePost'), default=[])
	num_replies = db.IntField(default=0)
	status = db.StringField(default='new')

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
		self.time_created = post_info.get('time_created')
		self.view_url = post_info.get('view_url')
		if not self.has_parent:
			self.discussion.modify(
				discussion_post=self,
				view_url=self.view_url)
		else:
			parent_post = MoodlePost.objects(moodle_id=post_info.get('parent_id')).first()
			if parent_post:
				if not self in parent_post.post_list:
					parent_post.post_list.append(self)
			else:
				parent_post = MoodlePost.objects(moodle_id=post_info.get('parent_id')).modify(
					post_list=[self],
					upsert=True,
					new=True)
				self.parent_post = parent_post
			parent_post.num_replies = len(parent_post.post_list)
			parent_post.save()
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

		print('Update moodle post #{}'.format(self.serial_id))

		return self

	def update_post_status(self, status_info):
		self.status = status_info.get('post_status')
		if not self.has_parent:
			self.discussion.modify(status=self.status)

		return self


class MoodleDiscussion(db.Document):
	serial_id = db.SequenceField()
	moodle_id = db.IntField(unique=True)
	discussion_id = db.IntField(unique=True)
	user = db.ReferenceField('MoodleUser')
	course = db.ReferenceField('MoodleCourse')
	forum = db.ReferenceField('MoodleForum')
	discussion_post = db.ReferenceField('MoodlePost')
	name = db.StringField(default='')
	subject = db.StringField(default='')
	message = db.StringField(default='')
	created = db.IntField(default=0)
	time_modified = db.IntField(default=0)
	user_modified = db.IntField(default=0) # ? ReferenceField
	num_replies = db.IntField(default=0)
	view_url = db.StringField(default='')
	post_list = db.ListField(db.ReferenceField('MoodlePost'), default=[])
	status = db.StringField(default='new')


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

		print('Update moodle discussion #{}'.format(self.serial_id))

		return self


class MoodleForum(db.Document):
	serial_id = db.SequenceField()
	moodle_id = db.IntField(unique=True)
	course = db.ReferenceField('MoodleCourse')
	type = db.StringField(default='')
	name = db.StringField(default='')
	intro = db.StringField(default='')
	scale = db.IntField(default=0)
	discussion_list = db.ListField(db.ReferenceField('MoodleDiscussion'), default=[])

	def get_info(self):
		return self.to_json()

	def update_forum(self, forum_info):
		self.type = forum_info.get('type')
		self.name = forum_info.get('name')
		self.intro = forum_info.get('intro')
		self.scale = forum_info.get('scale')

		print('Update moodle forum #{}'.format(self.serial_id))

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
	forum_list = db.ListField(db.ReferenceField('MoodleForum'), default=[])
	forum_count = db.IntField(default=0)

	def get_info(self):
		return self.to_json()

	def update_course(self, course_info, course_forum_list):
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
		self.forum_list = course_forum_list
		self.forum_count = len(self.forum_list)

		print('Update moodle course #{}: {}'.format(self.serial_id, self.short_name))

		return self


class MoodleUser(db.Document):
	serial_id = db.SequenceField()
	moodle_id = db.IntField()
	full_name = db.StringField(default='')
	user_url = db.StringField(default='')
	user_picture_url = db.StringField(default='')
	course_grade_dict= db.DictField(default={})

	def get_info(self):
		return self.to_json()

	def update_course_grade(self, user_course_grade):
		self.course_grade_dict.update(user_course_grade)

		print('Update moodle user course grade #{}'.format(self.serial_id))

		return self


class MoodleTeacher(BaseTeacher):
	moodle_url = db.StringField(default='')
	moodle_id = db.IntField()
	token = db.StringField(default='')
	username = db.StringField(default='')
	full_name = db.StringField(default='')
	user_picture_url = db.StringField(default='')
	course_list = db.ListField(db.ReferenceField('MoodleCourse'), default=[])
	filtration_set = db.ReferenceField('FiltrationSet')

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

		print('Update moodle teacher #{}: {}'.format(self.serial_id, self.full_name))

		return self

	def update_user_courses(self, user_course_list):
		self.course_list = user_course_list

		print('Update moodle teacher courses #{}'.format(self.serial_id))

		return self

	def filter_and_sort_discussions(self):
		# filter
		# 1. course
		discussions_list = MoodleDiscussion.objects(course__in=self.course_list)

		return discussions_list

	def filter_and_sort_posts(self):
		# filter
		# 1. course
		posts_list = MoodlePost.objects(course__in=self.course_list)

		return posts_list
