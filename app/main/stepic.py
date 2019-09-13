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
			'bsc_fokin_stepic_oauth',
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
		full_name = response['users'][0]['full_name']
		avatar_url = response['users'][0]['avatar']
		stepic_id = response['users'][0]['id']

		return str(stepic_id), full_name, avatar_url


class StepicApi:

	def __init__(self):
		self.__token = self.__authorize()

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
		stepic_profile = self.__fetch_object(STEPIC_USERS, user_id)
		teacher = Teacher(
			stepic_id=user_id,
			full_name=stepic_profile['full_name'],
			avatar_url=stepic_profile['avatar'])

		return teacher

	def get_course_info(self, course_id):
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
			steps=step_id_list)

		return course
