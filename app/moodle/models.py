from datetime import date, datetime, timedelta
from mongoengine.queryset.visitor import Q
from app.create_app import db
from app.main.models import BaseTeacher
from app.filtration.models import FiltrationSet


class MoodleFiltrationSet(FiltrationSet):
	course_list = db.ListField(db.ReferenceField('MoodleCourse'), default=[])
	tag_list = db.ListField(db.ReferenceField('MoodleTag'), default=[])
	author = db.ReferenceField('MoodleUser')

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
			'post_status': args.get('post_status')}

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
		self.course_list = [MoodleCourse.objects(moodle_id=int(course_id)).first() for course_id in filtration_set_info.get('course_id_list')] if filtration_set_info.get('course_id_list') else []
		self.tag_list = [MoodleTag.objects(moodle_id=int(tag_id)).first() for tag_id in filtration_set_info.get('tag_id_list')] if filtration_set_info.get('tag_id_list') else []
		self.author = MoodleUser.objects(serial_id=filtration_set_info.get('author_id')).first() if filtration_set_info.get('author_id') else None
		self.post_status = filtration_set_info.get('post_status')

		print('Update moodle filtration set #{}'.format(self.serial_id))

		return self

	# copy filtration_set_2 data to filtration_set_1
	def copy_filtration_set(self, filtration_set_1, filtration_set_2):
		filtration_set_1.date_from = filtration_set_2.date_from
		filtration_set_1.date_to = filtration_set_2.date_to
		filtration_set_1.date_order = filtration_set_2.date_order
		filtration_set_1.replies_from = filtration_set_2.replies_from
		filtration_set_1.replies_to = filtration_set_2.replies_to
		filtration_set_1.replies_order = filtration_set_2.replies_order
		filtration_set_1.progress_from = filtration_set_2.progress_from
		filtration_set_1.progress_to = filtration_set_2.progress_to
		filtration_set_1.progress_order = filtration_set_2.progress_order
		filtration_set_1.course_list = filtration_set_2.course_list
		filtration_set_1.tag_list = filtration_set_2.tag_list
		filtration_set_1.author = filtration_set_2.author
		filtration_set_1.post_status = filtration_set_2.post_status

		print('Copy moodle filtration_set #{} <-- #{}'.format(filtration_set_1.serial_id, filtration_set_2.serial_id))

		return filtration_set_1

	# импорт фильтра для Moodle
	def import_filtration_set(self, filtration_set_id):
		old_filtration_set = MoodleFiltrationSet(serial_id=filtration_set_id).first()
		self.copy_filtration_set(self, old_filtration_set).save()

		print('Import moodle filtration_set #{}'.format(old_filtration_set.serial_id))

		return self

	# экспорт фильтра для Moodle
	def export_filtration_set(self, title):
		new_filtration_set = MoodleFiltrationSet(title=title).save()
		self.copy_filtration_set(new_filtration_set, self).save()


		print('Export moodle filtration_set #{}'.format(new_filtration_set.serial_id))

		return self

	# url параметры
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

	# url параметры поля "Курсы"
	def get_courses_args_url(self):
		return '&'.join('course_ids[]={}'.format(course.moodle_id) for course in self.course_list)

	# url параметры поля "Теги"
	def get_tags_args_url(self):
		return '&'.join('tag_ids[]={}'.format(tag.moodle_id) for tag in self.tag_list)

	# url параметры поля "Автор"
	def get_author_args_url(self):
		return 'author_id={}'.format(self.author.serial_id if self.author else 0)


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
	tag_list = db.ListField(db.ReferenceField('MoodleTag'))
	post_list = db.ListField(db.ReferenceField('MoodlePost'), default=[])
	num_replies = db.IntField(required=True)
	status = db.StringField(required=True)
	progress = db.FloatField(required=True)

	def get_info(self):
		return self.to_json()

	def update_post(self, post_info):
		self.subject = post_info.get('subject')
		self.reply_subject = post_info.get('reply_subject')
		self.message = post_info.get('message')
		self.has_parent = post_info.get('has_parent')
		self.time_created = post_info.get('time_created')
		self.view_url = post_info.get('view_url')
		self.tag_list = [
			MoodleTag.objects(moodle_id=tag_info.get('id')).modify(
				moodle_id=tag_info.get('id'),
				tag_id=tag_info.get('tagid'),
				is_standard=tag_info.get('isstandard'),
				display_name=tag_info.get('displayname'),
				upsert=True,
				new=True)
			for tag_info in post_info.get('tags')]
		self.status = self.status if self.status else 'new' # Иначе не работает фильтрация по дефолтному значению
		self.progress = 0
		if not self.has_parent:
			self.discussion.modify(
				discussion_post=self,
				view_url=self.view_url,
				tag_list=self.tag_list,
				status=self.status,
				progress=self.progress)
		else:
			parent_post = MoodlePost.objects(moodle_id=post_info.get('parent_id')).first()
			if parent_post:
				if not self in parent_post.post_list:
					parent_post.post_list.append(self)
			else:
				parent_post = MoodlePost.objects(moodle_id=post_info.get('parent_id')).modify(
					post_list=[self],
					status='new',
					progress=0,
					upsert=True,
					new=True)
				self.parent_post = parent_post
			parent_post.num_replies = len(parent_post.post_list)
			parent_post.save()
		if post_info.get('rating'):
			self.rating = post_info.get('rating').get('rating')
			self.rating_count = post_info.get('rating').get('count')
			self.rating_label = post_info.get('rating').get('aggregatelabel')
		self.num_replies = self.num_replies if self.num_replies else 0 # Иначе не работает фильтрация по дефолтному значению

		print('Update moodle post #{}'.format(self.serial_id))

		return self

	def update_post_status(self, status_info):
		self.status = status_info.get('post_status')
		if not self.has_parent:
			self.discussion.modify(status=self.status)

		return self

	def update_post_progress(self):
		self.progress = round((self.user.course_grade_dict[str(self.course.moodle_id)] / self.course.grade_max * 100), 2) if self.course.grade_max else 0
		if not self.has_parent:
			self.discussion.modify(progress=self.progress)

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
	time_created = db.IntField(default=0)
	time_modified = db.IntField(default=0)
	user_modified = db.IntField(default=0) # ? ReferenceField
	num_replies = db.IntField(required=True)
	view_url = db.StringField(default='')
	tag_list = db.ListField(db.ReferenceField('MoodleTag'))
	post_list = db.ListField(db.ReferenceField('MoodlePost'), default=[])
	status = db.StringField(default='new')
	progress = db.FloatField(required=True)


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
		self.time_created = discussion_info.get('time_created')
		self.time_modified = discussion_info.get('time_modified')
		self.user_modified = discussion_info.get('user_modified')
		self.num_replies = discussion_info.get('num_replies')
		self.progress = self.progress if self.progress else 0

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
	grade_max = db.IntField()
	show_grades = db.BooleanField(default=False)
	start_date = db.IntField(default=0)
	cover = db.StringField(default='')
	forum_list = db.ListField(db.ReferenceField('MoodleForum'), default=[])
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
	filtration_set = db.ReferenceField('MoodleFiltrationSet')

	def get_info(self):
		return self.to_json()

	def update_teacher(self, teacher_info):
		self.username = teacher_info.get('username')
		self.full_name = teacher_info.get('fullname')
		self.user_picture_url = teacher_info.get('userpictureurl')
		filtration_set_title = '{} (по умолчанию)'.format(teacher_info.get('username'))
		self.filtration_set = MoodleFiltrationSet.objects(title=filtration_set_title).modify(
				title=filtration_set_title,
				date_from=datetime.fromisoformat((date.today() - timedelta(30)).isoformat()).timestamp(),
				date_to=datetime.fromisoformat((date.today() + timedelta(1)).isoformat()).timestamp(),
				upsert=True,
				new=True)

		print('Update moodle teacher #{}: {}'.format(self.serial_id, self.full_name))

		return self

	def update_user_courses(self, user_course_list):
		self.course_list = user_course_list

		print('Update moodle teacher courses #{}'.format(self.serial_id))

		return self

	def filter_and_sort_discussions(self, current_user):
		# filter
		filtration_set = current_user.filtration_set
		# 4. Курсы
		discussion_list = MoodleDiscussion.objects(course__in=filtration_set.course_list) if filtration_set.course_list else MoodleDiscussion.objects()
		# 1. Дата
		discussion_list = discussion_list.filter(Q(time_created__gte=filtration_set.date_from) & Q(time_created__lte=filtration_set.date_to))
		# 2. Ответы
		discussion_list = discussion_list.filter(Q(num_replies__gte=filtration_set.replies_from) & Q(num_replies__lte=filtration_set.replies_to))
		# 5. Теги
		discussion_list = discussion_list.filter(tag_list__in=[tag for tag in filtration_set.tag_list]) if filtration_set.tag_list else discussion_list
		# 6. Автор
		discussion_list = discussion_list.filter(user=filtration_set.author) if filtration_set.author else discussion_list
		# 7. Статус
		discussion_list = discussion_list.filter(status=filtration_set.post_status) if filtration_set.post_status != 'all' else discussion_list
		# 3. Прогресс
		for discussion in discussion_list:
			discussion.discussion_post.update_post_progress().save()
		discussion_list = discussion_list.filter(Q(progress__gte=filtration_set.progress_from) & Q(progress__lte=filtration_set.progress_to))
		# sort
		discussion_list = discussion_list.order_by(*filtration_set.get_sort_args_list())

		return discussion_list

	def filter_and_sort_posts(self, current_user):
		# filter
		filtration_set = current_user.filtration_set
		# 4. Курсы
		post_list = MoodlePost.objects(course__in=filtration_set.course_list) if filtration_set.course_list else MoodlePost.objects()
		# 1. Дата
		post_list = post_list.filter(Q(time_created__gte=filtration_set.date_from) & Q(time_created__lte=filtration_set.date_to))
		# 2. Ответы
		post_list = post_list.filter(Q(num_replies__gte=filtration_set.replies_from) & Q(num_replies__lte=filtration_set.replies_to))
		# 5. Теги
		post_list = post_list.filter(tag_list__in=[tag for tag in filtration_set.tag_list]) if filtration_set.tag_list else post_list
		# 6. Автор
		post_list = post_list.filter(user=filtration_set.author) if filtration_set.author else post_list
		# 7. Статус
		post_list = post_list.filter(status=filtration_set.post_status) if filtration_set.post_status != 'all' else post_list
		# 3. Прогресс
		for post in post_list:
			post.update_post_progress().save()
		post_list = post_list.filter(Q(progress__gte=filtration_set.progress_from) & Q(progress__lte=filtration_set.progress_to))
		# sort
		post_list = post_list.order_by(*filtration_set.get_sort_args_list())

		return post_list
