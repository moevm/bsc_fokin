from app.create_app import db
from app.main.models import BaseTeacher
from app.stepic.stepic_api import StepicApi
import re


class Course(db.Document):
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
		self.title=course_info['title']
		self.summary=course_info['summary']
		self.cover=course_info['cover']
		self.cert_reg_threshold=course_info['cert_reg_threshold']
		self.cert_dist_threshold=course_info['cert_dist_threshold']
		self.score=course_info['score']

		return self


class Option(db.EmbeddedDocument):
	sort = db.StringField(default='')
	order = db.StringField(default='')
	filter_gte = db.IntField(default=-1)
	filter_lte = db.IntField(default=-1)
	datetime_gte = db.StringField(default='-')
	datetime_lte = db.StringField(default='-')


class StepicTeacher(BaseTeacher):
	serial_id = db.SequenceField()
	stepic_id = db.IntField(unique=True)
	full_name = db.StringField(default='')
	avatar_url = db.StringField(default='')
	course_list = db.ListField(db.ReferenceField(Course), default=[])
	course_review_filter = db.IntField(default=-1)
	course_comment_filter = db.IntField(default=-1)
	review_option_list = db.ListField(db.EmbeddedDocumentField(Option),
									  default=[Option(sort='score', filter_gte=1, filter_lte=5),
											   Option(sort='user_reputation', order = '-', filter_gte=0),
											   Option(sort='create_date', order = '-')])
	comment_option_list = db.ListField(db.EmbeddedDocumentField(Option),
									   default=[Option(sort='reply_count', filter_gte=0),
												Option(sort='epic_count', order = '-', filter_gte=0),
												Option(sort='user_reputation', order = '-', filter_gte=0),
												Option(sort='abuse_count', filter_gte=0),
												Option(sort='time', order = '-')])

	def get_info(self):
		return self.to_json()

	def update_comment_filters(self, form):
		for i in range(5):
			self.comment_option_list[i] = Option(sort=form.get('sorting_{}'.format(i + 1)),
												 order=form.get('ordering_{}'.format(i + 1)),
												 filter_gte=form.get('filter_gte_{}'.format(i + 1)) if form.get('filter_gte_{}'.format(i + 1)) != '-' else -1,
 												 filter_lte=form.get('filter_lte_{}'.format(i + 1)) if form.get('filter_lte_{}'.format(i + 1)) != '-' else -1,
												 datetime_gte=form.get('datetime_gte_{}'.format(i + 1)) if form.get('datetime_gte_{}'.format(i + 1)) and re.fullmatch(r'\d{4}\-\d{2}\-\d{2}T\d{2}:\d{2}:\d{2}Z', form.get('datetime_gte_{}'.format(i + 1))) else '-',
												 datetime_lte=form.get('datetime_lte_{}'.format(i + 1)) if form.get('datetime_lte_{}'.format(i + 1)) and re.fullmatch(r'\d{4}\-\d{2}\-\d{2}T\d{2}:\d{2}:\d{2}Z', form.get('datetime_lte_{}'.format(i + 1))) else '-')
		self.course_comment_filter = form.get('course')

		return self

	def update_review_filters(self, form):
		for i in range(3):
			self.review_option_list[i] = Option(sort=form.get('sorting_{}'.format(i + 1)),
												order=form.get('ordering_{}'.format(i + 1)),
												filter_gte=form.get('filter_gte_{}'.format(i + 1)) if form.get('filter_gte_{}'.format(i + 1)) != '-' else -1,
												filter_lte=form.get('filter_lte_{}'.format(i + 1)) if form.get('filter_lte_{}'.format(i + 1)) != '-' else -1,
												datetime_gte=form.get('datetime_gte_{}'.format(i + 1)) if form.get('datetime_gte_{}'.format(i + 1)) and re.fullmatch(r'\d{4}\-\d{2}\-\d{2}T\d{2}:\d{2}:\d{2}Z', form.get('datetime_gte_{}'.format(i + 1))) else '-',
												datetime_lte=form.get('datetime_lte_{}'.format(i + 1)) if form.get('datetime_lte_{}'.format(i + 1)) and re.fullmatch(r'\d{4}\-\d{2}\-\d{2}T\d{2}:\d{2}:\d{2}Z', form.get('datetime_lte_{}'.format(i + 1))) else '-')
		self.course_review_filter = form.get('course')

		return self

	def get_comment_filters(self):
		return list(map(lambda x: '{}{}'.format(x.order, x.sort), self.comment_option_list))

	def get_review_filters(self):
		return list(map(lambda x: '{}{}'.format(x.order, x.sort), self.review_option_list))

	def filter_and_sort_comments(self):
		# filter
		# 1. course
		comment_list = Comment.objects(course__in=self.course_list) if self.course_comment_filter == -1 else Comment.objects(course=Course.objects(stepic_id=self.course_comment_filter).first())
		# 2. reply_count
		comment_reply_count_option = self.get_option_by_sort('reply_count', self.comment_option_list)
		comment_list = comment_list.filter(reply_count__gte=comment_reply_count_option.filter_gte) if comment_reply_count_option.filter_gte != -1 else comment_list
		comment_list = comment_list.filter(reply_count__lte=comment_reply_count_option.filter_lte) if comment_reply_count_option.filter_lte != -1 else comment_list
		# 3. epic_count
		comment_epic_count_option = self.get_option_by_sort('epic_count', self.comment_option_list)
		comment_list = comment_list.filter(epic_count__gte=comment_epic_count_option.filter_gte) if comment_epic_count_option.filter_gte != -1 else comment_list
		comment_list = comment_list.filter(epic_count__lte=comment_epic_count_option.filter_lte) if comment_epic_count_option.filter_lte != -1 else comment_list
		# 4. user_reputation
		comment_user_reputation_option = self.get_option_by_sort('user_reputation', self.comment_option_list)
		comment_list = comment_list.filter(user_reputation__gte=comment_user_reputation_option.filter_gte) if comment_user_reputation_option.filter_gte != -1 else comment_list
		comment_list = comment_list.filter(user_reputation__lte=comment_user_reputation_option.filter_lte) if comment_user_reputation_option.filter_lte != -1 else comment_list
		# 5. abuse_count
		comment_abuse_count_option = self.get_option_by_sort('abuse_count', self.comment_option_list)
		comment_list = comment_list.filter(abuse_count__gte=comment_abuse_count_option.filter_gte) if comment_abuse_count_option.filter_gte != -1 else comment_list
		comment_list = comment_list.filter(abuse_count__lte=comment_abuse_count_option.filter_lte) if comment_abuse_count_option.filter_lte != -1 else comment_list
		# 6. time
		comment_time_option = self.get_option_by_sort('time', self.comment_option_list)
		comment_list = comment_list.filter(time__gte=comment_time_option.datetime_gte) if comment_time_option.datetime_gte != '-' else comment_list
		comment_list = comment_list.filter(time__lte=comment_time_option.datetime_lte) if comment_time_option.datetime_lte != '-' else comment_list
		# sort
		comment_list = comment_list.order_by(*self.get_comment_filters())

		return comment_list

	def filter_and_sort_reviews(self):
		# filter
		# 1. course
		review_list = Review.objects(course__in=self.course_list) if self.course_review_filter == -1 else Review.objects(course=Course.objects(stepic_id=self.course_review_filter).first())
		# 2. score
		review_score_option = self.get_option_by_sort('score', self.review_option_list)
		review_list = review_list.filter(score__gte=review_score_option.filter_gte) if review_score_option.filter_gte != -1 else review_list
		review_list = review_list.filter(score__lte=review_score_option.filter_lte) if review_score_option.filter_lte != -1 else review_list
		# 3. user_reputation
		review_user_reputation_option = self.get_option_by_sort('user_reputation', self.review_option_list)
		review_list = review_list.filter(user_reputation__gte=review_user_reputation_option.filter_gte) if review_user_reputation_option.filter_gte != -1 else review_list
		review_list = review_list.filter(user_reputation__lte=review_user_reputation_option.filter_lte) if review_user_reputation_option.filter_lte != -1 else review_list
		# 3. create_date
		review_create_date_option = self.get_option_by_sort('create_date', self.review_option_list)
		review_list = review_list.filter(create_date__gte=review_create_date_option.datetime_gte) if review_create_date_option.datetime_gte != '-' else review_list
		review_list = review_list.filter(create_date__lte=review_create_date_option.datetime_lte) if review_create_date_option.datetime_lte != '-' else review_list
		# sort
		review_list = review_list.order_by(*self.get_review_filters())

		return review_list

	def get_option_by_sort(self, sort, option_list):
		for option in option_list:
			if option.sort == sort:
				return option


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
		# update reputation in users comments and reviews
		user_comment_list = Comment.objects(user=self)
		for comment in user_comment_list:
			comment.user_reputation = self.reputation
			comment.save()
		user_review_list = Review.objects(user=self)
		for review in user_review_list:
			review.user_reputation = self.reputation
			review.save()

		return self

	def add_step(self, comment_info):
		user_course = self.courses.get(str(comment_info['course_id']))
		if user_course:
			user_course.add_step(comment_info)
		else:
			self.courses[str(comment_info['course_id'])]=UserCourse().add_step(comment_info)

		return self

	def add_course(self, review_info):
		user_course = self.courses.get(str(review_info['course_id']))
		if not user_course:
			self.courses[str(review_info['course_id'])]=UserCourse()

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


class Review(db.Document):
	serial_id = db.SequenceField()
	stepic_id = db.IntField(unique=True)
	user = db.ReferenceField(User)
	user_reputation = db.IntField(default=0)
	course = db.ReferenceField(Course)
	create_date = db.StringField(default='')
	update_date = db.StringField(default='')
	text = db.StringField(default='')
	score = db.IntField(default=0)

	def get_info(self):
		return self.to_json()

	def update_review(self, comment_info):
		self.stepic_id=comment_info['stepic_id']
		self.create_date=comment_info['create_date']
		self.update_date=comment_info['update_date']
		self.text=comment_info['text']
		self.score=comment_info['score']

		return self
