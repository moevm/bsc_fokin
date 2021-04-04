from datetime import date, datetime, timedelta
from dateutil.parser import parse
from mongoengine.queryset.visitor import Q
from app.create_app import db
from app.main.models import BaseTeacher
from app.stepic.stepic_api import StepicApi
from app.filtration.models import FiltrationSet


class StepicFiltrationSet(FiltrationSet):
	course_list = db.ListField(db.ReferenceField('StepicCourse'), default=[])
	# поле "Репутация"
	reputation_from = db.IntField(default=0)
	reputation_to = db.IntField(default=100000)
	reputation_order = db.StringField(default='-')
	# поле "Автор"
	author = db.ReferenceField('StepicUser')
	# поле "Статус" комментария
	comment_status = db.StringField(default='all')

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
			'reputation_from': args.get('reputation[from]'),
			'reputation_to': args.get('reputation[to]'),
			'reputation_order': args.get('reputation[order]'),
			'course_id_list': args.getlist('course_ids[]'),
			'author_id': args.get('author_id'),
			'comment_status': args.get('comment_status')}

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
		self.reputation_from = filtration_set_info.get('reputation_from')
		self.reputation_to = filtration_set_info.get('reputation_to')
		self.reputation_order = filtration_set_info.get('reputation_order')
		self.course_list = [StepicCourse.objects(stepic_id=int(course_id)).first() for course_id in filtration_set_info.get('course_id_list')] if filtration_set_info.get('course_id_list') else []
		self.author = StepicUser.objects(serial_id=filtration_set_info.get('author_id')).first() if filtration_set_info.get('author_id') else None
		self.comment_status = filtration_set_info.get('comment_status')

		print('Update stepic filtration set #{}'.format(self.serial_id))

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
		filtration_set_1.reputation_from = filtration_set_2.reputation_from
		filtration_set_1.reputation_to = filtration_set_2.reputation_to
		filtration_set_1.reputation_order = filtration_set_2.reputation_order
		filtration_set_1.course_list = filtration_set_2.course_list
		filtration_set_1.author = filtration_set_2.author
		filtration_set_1.comment_status = filtration_set_2.comment_status

		print('Copy stepic filtration_set #{} <-- #{}'.format(filtration_set_1.serial_id, filtration_set_2.serial_id))

		return filtration_set_1

	# импорт фильтра для Stepic
	def import_filtration_set(self, filtration_set_id):
		old_filtration_set = StepicFiltrationSet.objects(serial_id=filtration_set_id).first()
		self.copy_filtration_set(self, old_filtration_set).save()

		print('Import stepic filtration_set #{}'.format(old_filtration_set.serial_id))

		return self

	# экспорт фильтра для Stepic
	def export_filtration_set(self, title):
		new_filtration_set = StepicFiltrationSet(title=title).save()
		self.copy_filtration_set(new_filtration_set, self).save()


		print('Export stepic filtration_set #{}'.format(new_filtration_set.serial_id))

		return self

	# url параметры
	def get_url(self):
		url = '?{}&{}&{}&{}&{}'.format(
			self.get_date_args_url(),
			self.get_replies_args_url(),
			# self.get_progress_args_url(),
			self.get_reputation_args_url(),
			self.get_courses_args_url(),
			self.get_author_args_url(),
			self.get_comment_status_args_url())

		return url

	# url параметры поля "Репутация"
	def get_reputation_args_url(self):
		reputation_args_url = 'reputation[from]={}&reputation[to]={}&reputation[order]={}'.format(
			self.reputation_from,
			self.reputation_to,
			self.reputation_order)

		return reputation_args_url

	# url параметры поля "Курсы"
	def get_courses_args_url(self):
		return '&'.join('course_ids[]={}'.format(course.stepic_id) for course in self.course_list)

	# url параметры поля "Автор"
	def get_author_args_url(self):
		return 'author_id={}'.format(self.author.serial_id if self.author else 0)

	# url параметры поля "Статус"
	def get_comment_status_args_url(self):
		return 'comment_status={}'.format(self.comment_status)

	# параметры сортировки по полям: "Дата", "Ответы", "Прогресс", "Репутация"
	def get_sort_args_list(self):
		sort_args_list = [
			'{}{}'.format(self.date_order, 'time_created'),
			'{}{}'.format(self.date_order, 'create_date'),
			'{}{}'.format(self.replies_order, 'num_replies'),
			'{}{}'.format(self.progress_order, 'progress'),
			'{}{}'.format(self.reputation_order, 'user_reputation')]

		return sort_args_list


class StepicReview(db.Document):
	serial_id = db.SequenceField()
	stepic_id = db.IntField(unique=True)
	user = db.ReferenceField('StepicUser')
	user_reputation = db.IntField(default=0)
	course = db.ReferenceField('StepicCourse')
	create_date = db.IntField(default=0)
	update_date = db.IntField(default=0)
	text = db.StringField(default='')
	score = db.IntField(default=0)
	status = db.StringField(default='new')

	def get_info(self):
		return self.to_json()

	def update_review(self, comment_info):
		self.stepic_id=comment_info['stepic_id']
		self.create_date=parse(comment_info['create_date']).timestamp()
		self.update_date=parse(comment_info['update_date']).timestamp()
		self.text=comment_info['text']
		self.score=comment_info['score']
		self.status = self.status if self.status else 'new' # Иначе не работает фильтрация по дефолтному значению

		print('Update stepic review #{}'.format(self.serial_id))

		return self


class StepicComment(db.Document):
	serial_id = db.SequenceField()
	stepic_id = db.IntField(unique=True)
	parent_id = db.IntField()
	step_id = db.IntField()
	user = db.ReferenceField('StepicUser')
	user_reputation = db.IntField(default=0)
	course = db.ReferenceField('StepicCourse')
	user_role = db.StringField(default='')
	time = db.IntField(default=0)
	last_time = db.IntField(default=0)
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
	status = db.StringField(default='new')

	def get_info(self):
		return self.to_json()

	def update_comment(self, comment_info):
		self.stepic_id = comment_info['stepic_id']
		self.parent_id = comment_info['parent_id']
		self.step_id = comment_info['step_id']
		self.user_role = comment_info['user_role']
		self.time = parse(comment_info['time']).timestamp()
		self.last_time = parse(comment_info['last_time']).timestamp()
		self.text = comment_info['text']
		# self.replies = comment_info['replies']
		self.reply_count = comment_info['reply_count']
		self.is_deleted = comment_info['is_deleted']
		self.is_pinned = comment_info['is_pinned']
		self.is_staff_replied = comment_info['is_staff_replied']
		self.is_reported = comment_info['is_reported']
		self.attachments = comment_info['attachments']
		self.epic_count = comment_info['epic_count']
		self.abuse_count = comment_info['abuse_count']
		self.status = self.status if self.status else 'new' # Иначе не работает фильтрация по дефолтному значению

		print('Update stepic comment #{}'.format(self.serial_id))

		return self

	def update_comment_status(self, status_info):
		self.status = status_info.get('comment_status')

		return self


class StepicUserStep(db.EmbeddedDocument):
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


class StepicUserCourse(db.EmbeddedDocument):
	score = db.IntField(default=0)
	steps = db.MapField(db.EmbeddedDocumentField('StepicUserStep'))

	def get_info(self):
		return self.to_json()

	def add_step(self, comment_info):
		step_id = str(comment_info.get('step_id'))
		user_step = self.steps.get(step_id)
		if not user_step:
			self.steps[step_id]=StepicUserStep()

		return self

	def update_step_grades(self, course_grades):
		self.score=course_grades.get('score')
		results = course_grades.get('results')
		for step_grades in results:
			step_id = str(results.get(step_grades).get('step_id'))
			if step_id in self.steps:
				self.steps[step_id].update_user_step(results.get(step_grades))

		return self


class StepicCourse(db.Document):
	serial_id = db.SequenceField()
	stepic_id = db.IntField(unique=True)
	title = db.StringField(default='')
	summary = db.StringField(default='')
	cover = db.StringField(default='/static/images/stepic_course_cover.png')
	cert_reg_threshold = db.IntField(default=0)
	cert_dist_threshold = db.IntField(default=0)
	score = db.IntField(default=0)

	def get_info(self):
		return self.to_json()

	def update_course(self, course_info):
		self.title=course_info.get('title')
		self.summary=course_info.get('summary')
		self.cover=course_info.get('cover')
		self.cert_reg_threshold=course_info.get('cert_reg_threshold')
		self.cert_dist_threshold=course_info.get('cert_dist_threshold')
		self.score=course_info.get('score')

		print('Update stepic course #{}'.format(self.serial_id))

		return self


class StepicUser(db.Document):
	serial_id = db.SequenceField()
	stepic_id = db.IntField(unique=True)
	full_name = db.StringField(default='')
	avatar_url = db.StringField(default='')
	reputation = db.IntField(default=0)
	courses = db.MapField(db.EmbeddedDocumentField('StepicUserCourse'))

	def get_info(self):
		return self.to_json()

	def update_user(self, user_info):
		self.full_name=user_info.get('full_name')
		self.avatar_url=user_info.get('avatar')
		self.reputation=user_info.get('reputation')
		# update reputation in users comments and reviews
		user_comment_list = StepicComment.objects(user=self)
		for comment in user_comment_list:
			comment.user_reputation = self.reputation
			comment.save()
		user_review_list = StepicReview.objects(user=self)
		for review in user_review_list:
			review.user_reputation = self.reputation
			review.save()

		print('Update stepic user #{}'.format(self.serial_id))

		return self

	def add_step(self, comment_info):
		course_id = str(comment_info.get('course_id'))
		user_course = self.courses.get(course_id)
		if user_course:
			user_course.add_step(comment_info)
		else:
			self.courses[course_id]=StepicUserCourse().add_step(comment_info)

		return self

	def add_course(self, review_info):
		course_id = str(review_info.get('course_id'))
		user_course = self.courses.get(course_id)
		if not user_course:
			self.courses[course_id]=StepicUserCourse()

		return self

	def update_course_grades(self, token):
		stepic_api = StepicApi(token)
		for course_id in self.courses:
			course_grades = stepic_api.get_user_course_grades(course_id, self.stepic_id)
			if course_grades:
				self.courses[course_id].update_step_grades(course_grades[0])

		return self


class StepicTeacher(BaseTeacher):
	stepic_id = db.IntField()
	token = db.StringField(default='')
	full_name = db.StringField(default='')
	avatar_url = db.StringField(default='')
	course_list = db.ListField(db.ReferenceField('StepicCourse'), default=[])
	filtration_set = db.ReferenceField('StepicFiltrationSet')

	def get_info(self):
		return self.to_json()

	def update_teacher(self, teacher_info):
		self.full_name = teacher_info.get('full_name')
		self.avatar_url = teacher_info.get('avatar')
		filtration_set_title = '{} (по умолчанию)'.format(teacher_info.get('full_name'))
		self.filtration_set = StepicFiltrationSet.objects(title=filtration_set_title).modify(
				title=filtration_set_title,
				date_from=datetime.fromisoformat((date.today() - timedelta(30)).isoformat()).timestamp(),
				date_to=datetime.fromisoformat((date.today() + timedelta(1)).isoformat()).timestamp(),
				upsert=True,
				new=True)

		print('Update stepic teacher #{}: {}'.format(self.serial_id, self.full_name))

		return self

	def filter_and_sort_comments(self):
		# filter
		filtration_set = self.filtration_set
		# 5. Курсы
		comment_list = StepicComment.objects(course__in=filtration_set.course_list) if filtration_set.course_list else StepicComment.objects()
		# 1. Дата
		comment_list = comment_list.filter(Q(time__gte=filtration_set.date_from) & Q(time__lte=filtration_set.date_to))
		# 2. Ответы
		comment_list = comment_list.filter(Q(reply_count__gte=filtration_set.replies_from) & Q(reply_count__lte=filtration_set.replies_to))
		# 3. Прогресс - отключено
		# 4. Репутация
		comment_list = comment_list.filter(Q(user_reputation__gte=filtration_set.reputation_from) & Q(user_reputation__lte=filtration_set.reputation_to))
		# 6. Автор
		comment_list = comment_list.filter(user=filtration_set.author) if filtration_set.author else comment_list
		# 7. Статус
		comment_list = comment_list.filter(status=filtration_set.comment_status) if filtration_set.comment_status != 'all' else comment_list
		# sort
		comment_list = comment_list.order_by(*filtration_set.get_sort_args_list())

		return comment_list

	def filter_and_sort_reviews(self):
		# filter
		filtration_set = self.filtration_set
		# 4. Курсы
		review_list = StepicReview.objects(course__in=filtration_set.course_list) if filtration_set.course_list else StepicReview.objects()
		# 1. Дата
		review_list = review_list.filter(Q(create_date__gte=filtration_set.date_from) & Q(create_date__lte=filtration_set.date_to))
		# 2. Прогресс - отключено
		# 3. Репутация
		review_list = review_list.filter(Q(user_reputation__gte=filtration_set.reputation_from) & Q(user_reputation__lte=filtration_set.reputation_to))
		# sort
		review_list = review_list.order_by(*filtration_set.get_sort_args_list())

		return review_list
