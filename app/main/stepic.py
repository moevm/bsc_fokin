from app.create_app import oauth
from app.main.models import Course, Teacher
import config.config_reader as cr
import requests

STEPIC_USERS = 'user'
STEPIC_COURSES = 'course'
STEPIC_SECTIONS = 'section'
STEPIC_UNITS = 'unit'
STEPIC_LESSONS = 'lesson'
STEPIC_STEPS = 'step'
STEPIC_PROGRESSES = 'progresse'


class StepicOauth:

	def __init__(self):
		self.app = oauth.remote_app(
			'stepic_oauth_auto',
			request_token_url=None,
			access_token_url='https://stepik.org/oauth2/token/',
			authorize_url='https://stepik.org/oauth2/authorize/',
			consumer_key=cr.get_stepic_oauth_client_id(),
			consumer_secret=cr.get_stepic_oauth_client_secret(),
			request_token_params={'scope': 'read write'},
			access_token_method='POST')


class StepicAgent:

	def __init__(self, token):
		self.__token = token

	def __send_get_request(self, url, data={}):
		response = requests.get(
			url,
			data=data,
			headers={'Authorization': 'Bearer {}'.format(self.__token)}).json()

		return response

	def get_profile_info(self):
		url = 'https://stepik.org/api/stepics/1'
		response = self.__send_get_request(url)
		name = response['users'][0]['full_name']
		avatar = response['users'][0]['avatar']
		stepic_id = response['users'][0]['id']

		return name, avatar, str(stepic_id)


class StepicApi:

	def __init__(self):
		self.__token = self.__authorize()

	# **************************************************************************
	# Private functions
	# **************************************************************************
	def __authorize(self):
		auth = requests.auth.HTTPBasicAuth(
			cr.get_stepic_api_client_id(),
			cr.get_stepic_api_client_secret())
		response = requests.post(
			'https://stepik.org/oauth2/token/',
			data={'grant_type': 'client_credentials'},
			auth=auth)
		token = response.json().get('access_token', None)

		if not token:
			print('Unable to authorize with provided credentials')

		return token


	def __parse_user_steps(self, steps, labs, results, student_id):
		student_labs = {}

		for lesson in results.keys():
			step_id = str(results[lesson]['step_id'])
			lesson_id = lesson.split('-')[0]
			step_position = lesson.split('-')[1]
			# add step to the group total stat
			if not steps.get(step_id):
				steps[step_id] = {
					'lesson_id': lesson_id,
					'step_position': step_position,
					'passed': 0}
			if results[lesson]['is_passed']:
				steps[step_id]['passed'] += 1
			# add step to the group lab stat
			if (labs.get(lesson_id) and
				int(step_position) == ((student_id % labs[lesson_id]['variants']) + 1)):

				student_labs[lesson_id] = {'step_id': step_id}
				if not labs[lesson_id]['steps'].get(step_id):
					labs[lesson_id]['steps'][step_id] = {
						'lesson_id': lesson_id,
						'step_position': step_position,
						'learners': 0,
						'passed': 0}
				labs[lesson_id]['steps'][step_id]['learners'] += 1
				if results[lesson]['is_passed']:
					labs[lesson_id]['steps'][step_id]['passed'] += 1

		return {
			'steps': steps,
			'labs': labs,
			'student_labs': student_labs}

	# **************************************************************************
	# Private request functions
	# **************************************************************************
	def __fetch_object(self, obj_class, obj_id):
		url = 'https://stepik.org/api/{}s/{}'.format(obj_class, obj_id)
		response = requests.get(
			url,
			headers={'Authorization': 'Bearer {}'.format(self.__token)}).json()

		return response['{}s'.format(obj_class)][0]

	def __fetch_objects(self, obj_class, obj_ids):
		objs = []
		step_size = 30
		for i in range(0, len(obj_ids), step_size):
			obj_ids_slice = obj_ids[i:i + step_size]
			url = 'https://stepik.org/api/{}s?{}'.format(
				obj_class,
				'&'.join('ids[]={}'.format(obj_id) for obj_id in obj_ids_slice))
			response = requests.get(
				url,
				headers={'Authorization': 'Bearer {}'.format(self.__token)}).json()
			objs += response['{}s'.format(obj_class)]

		return objs

	def __fetch_course_grades(self, course_id, user_id):
		url = 'https://stepik.org/api/course-grades?course={}&user={}'.format(course_id, user_id)
		response = requests.get(
			url,
			headers={'Authorization': 'Bearer {}'.format(self.__token)}).json()

		return response['course-grades'][0]

	def __fetch_course_grades_by_class(self, course_id, class_id, page):
		url = 'https://stepik.org/api/course-grades?course={}&klass={}&page={}'.format(course_id, class_id, page)
		response = requests.get(
			url,
			headers={'Authorization': 'Bearer {}'.format(self.__token)}).json()

		return response

	def __fetch_submissions(self, step_id, user_id, page):
		url = 'https://stepik.org/api/submissions?step={}&user={}&page={}'.format(step_id, user_id, page)
		response = requests.get(
			url,
			headers={'Authorization': 'Bearer {}'.format(self.__token)}).json()

		return response

	# **************************************************************************
	# Public functions
	# **************************************************************************
	def get_teacher_info(self, user_id):
		"""
		Fetches teacher info

		Args:
			user_id:

		Returns:
			Teacher
		"""
		stepic_profile = self.__fetch_object(STEPIC_USERS, user_id)
		teacher = Teacher(
			stepic_id=user_id,
			full_name=stepic_profile['full_name'],
			avatar_url=stepic_profile['avatar'])

		return teacher

	def get_course_info(self, course_id):
		"""Отдает инфо о выбранном курсе, возвращает объект Course"""
		stepic_course = self.__fetch_object(STEPIC_COURSES, course_id)
		sections = self.__fetch_objects(STEPIC_SECTIONS, stepic_course['sections'])

		unit_ids = [unit for section in sections for unit in section['units']]
		units = self.__fetch_objects(STEPIC_UNITS, unit_ids)

		lesson_ids = [unit['lesson'] for unit in units]
		lessons = self.__fetch_objects(STEPIC_LESSONS, lesson_ids)

		step_ids = [step for lesson in lessons for step in lesson['steps']]
		steps = self.__fetch_objects(STEPIC_STEPS, step_ids)

		step_id_list = [str(step['id']) for step in steps if step['worth']]

		lab_unit_ids = [section['units'][-1] for section in sections]
		lab_units = self.__fetch_objects(STEPIC_UNITS, lab_unit_ids)

		lab_lesson_ids = [lab_unit['lesson'] for lab_unit in lab_units]
		lab_lessons = self.__fetch_objects(STEPIC_LESSONS, lab_lesson_ids)

		labs = {
			str(lab_lesson['id']): {
				'title': lab_lesson['title'],
				'variants': len(lab_lesson['steps']),
				'steps': {}}
			for lab_lesson in lab_lessons}

		if stepic_course['progress']:
			score = self.__fetch_object(STEPIC_PROGRESSES, stepic_course['progress'])['cost']
		else:
			progress_ids = [step['progress'] for step in steps]
			progresses = self.__fetch_objects(STEPIC_PROGRESSES, progress_ids)
			score = sum([progress['cost'] for progress in progresses])

		course = Course(
			stepic_id=course_id,
			title=stepic_course['title'],
			summary=stepic_course['summary'],
			cover='https://stepik.org{}'.format(stepic_course['cover']),
			cert_reg_threshold=stepic_course['certificate_regular_threshold'],
			cert_dist_threshold=stepic_course['certificate_distinction_threshold'],
			score=score,
			steps=step_id_list,
			labs=labs)

		return course

	def get_group_info(self, course_id, student_dict):
		"""
		Fetches group info about students, labs and steps

		Args:
			course_id:
			student_dict:

		Returns:
			dict
		"""
		cert_reg = 0
		cert_dist = 0
		students = {}
		steps = {}
		course = Course.objects(stepic_id=course_id).first()
		labs = course.labs

		for learners, user_id in enumerate(student_dict.keys()):
			user = self.__fetch_course_grades(
				course_id,
				user_id)

			students[user_id] = {
				'full_name': student_dict[user_id]['full_name'],
				'student_id': int(student_dict[user_id]['student_id']),
				'score': user['score'],
				'date_joined': user['date_joined'],
				'last_viewed': user['last_viewed'],
				'cert_reg_date': user['certificate_issue_regular_date'],
				'cert_dist_date': user['certificate_issue_distinction_date']}

			if user['certificate_issue_distinction_date']:
				cert_dist += 1
			elif user['certificate_issue_regular_date']:
				cert_reg += 1

			parsed_results = self.__parse_user_steps(
			 	steps,
				labs,
				user['results'],
				students[user_id]['student_id'])
			steps = parsed_results['steps']
			labs = parsed_results['labs']
			students[user_id]['labs'] = parsed_results['student_labs']

		return {
			'students': students,
			'learners': learners,
			'cert_reg': cert_reg,
			'cert_dist': cert_dist,
			'steps': steps,
			'labs': labs}

	def get_group_info_by_class(self, course_id, class_id, student_dict):
		"""
		Fetches group info about students, labs and steps with using stepic class

		Args:
			course_id:
			class_id:
			student_dict:

		Returns:
			dict
		"""
		page = 1
		learners = 0
		cert_reg = 0
		cert_dist = 0
		students = {}
		steps = {}
		course = Course.objects(stepic_id=course_id).first()
		labs = course.labs

		while page:
			response = self.__fetch_course_grades_by_class(
				course_id,
				class_id,
				page)
			meta = response["meta"]
			course_grades = response['course-grades']

			for user in course_grades:
				user_id = str(user['user'])
				if not student_dict.get(user_id):
					continue

				students[user_id] = {
					'full_name': student_dict[user_id]['full_name'],
					'student_id': int(student_dict[user_id]['student_id']),
					'score': user['score'],
					'date_joined': user['date_joined'],
					'last_viewed': user['last_viewed'],
					'cert_reg_date': user['certificate_issue_regular_date'],
					'cert_dist_date': user['certificate_issue_distinction_date']}

				learners += 1
				if user['certificate_issue_distinction_date']:
					cert_dist += 1
				elif user['certificate_issue_regular_date']:
					cert_reg += 1

				parsed_results = self.__parse_user_steps(
				 	steps,
					labs,
					user['results'],
					students[user_id]['student_id'])
				steps = parsed_results['steps']
				labs = parsed_results['labs']
				students[user_id]['labs'] = parsed_results['student_labs']

			page = page + 1 if meta['has_next'] else 0

		return {
			'students': students,
			'learners': learners,
			'cert_reg': cert_reg,
			'cert_dist': cert_dist,
			'steps': steps,
			'labs': labs}

	def get_first_solution_dates(self, user_id, steps):
		"""
		Fetches dates of the first / first correct solution for user

		Args:
			user_id:
			steps:

		Returns:
			dict
		"""
		first_solution_date = None
		first_correct_solution_date = None

		for step_id in steps:
			page = 1

			while page:
				response = self.__fetch_submissions(
					step_id,
					user_id,
					page)
				meta = response["meta"]
				submissions = response['submissions']

				for submission in submissions:
					if (first_solution_date == None or
							submission['time'] < first_solution_date):
						first_solution_date = submission['time']

					if submission['status'] == 'correct':
						first_correct_solution_date = first_solution_date

				page = page + 1 if meta['has_next'] else 0

		dates = {
			'first_solution': first_solution_date,
			'first_correct_solution': first_correct_solution_date}

		return dates
