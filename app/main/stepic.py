from app.create_app import oauth
from app.main.models import Course, Teacher
import config.config_reader as cr
import requests

STEPIC_SECTIONS = 'section'
STEPIC_UNITS = 'unit'
STEPIC_LESSONS = 'lesson'
STEPIC_STEPS = 'step'
STEPIC_PROGRESSES = 'progresse'
STEPIC_COURSE_GRADES = 'course-grades'
STEPIC_USERS = 'user'


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

class StepicApi:

	def __init__(self, token):
		self.__token = token

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

	# def __fetch_course_grades(self, course_id, user_id):
	# 	url = 'https://stepik.org/api/course-grades?course={}&user={}'.format(course_id, user_id)
	# 	response = requests.get(
	# 		url,
	# 		headers={'Authorization': 'Bearer {}'.format(self.__token)}).json()
	#
	# 	return response['course-grades'][0]

	def __fetch_current_user_profile(self):
		url = 'https://stepik.org/api/stepics/1'
		response = requests.get(
			url,
			headers={'Authorization': 'Bearer {}'.format(self.__token)}).json()

		return response['users'][0]

	def __fetch_courses(self, user_id, page):
		url = 'https://stepik.org/api/courses?teacher={}&page={}'.format(user_id, page)
		response = requests.get(
			url,
			headers={'Authorization': 'Bearer {}'.format(self.__token)}).json()

		return response

	def __fetch_comments(self, course_id, page):
		url = 'https://stepik.org/api/comments?course={}&page={}'.format(course_id, page)
		print(url)
		response = requests.get(
			url,
			headers={'Authorization': 'Bearer {}'.format(self.__token)}).json()

		return response

	# **************************************************************************
	# Public functions
	# **************************************************************************
	def get_current_user_profile(self):
		return self.__fetch_current_user_profile()

	def get_users_info(self, user_id_list):
		return self.__fetch_objects(STEPIC_USERS, user_id_list)

	def get_course_score(self, stepic_course):
		if stepic_course['progress']:
			score = self.__fetch_object(STEPIC_PROGRESSES, stepic_course['progress'])['cost']
		else:
			sections = self.__fetch_objects(STEPIC_SECTIONS, stepic_course['sections'])
			# ******************************************************************
			unit_ids = [unit for section in sections for unit in section['units']]
			units = self.__fetch_objects(STEPIC_UNITS, unit_ids)
			# ******************************************************************
			lesson_ids = [unit['lesson'] for unit in units]
			lessons = self.__fetch_objects(STEPIC_LESSONS, lesson_ids)
			# ******************************************************************
			step_ids = [step for lesson in lessons for step in lesson['steps']]
			steps = self.__fetch_objects(STEPIC_STEPS, step_ids)
			# ******************************************************************
			progress_ids = [step['progress'] for step in steps]
			progresses = self.__fetch_objects(STEPIC_PROGRESSES, progress_ids)
			score = sum([progress['cost'] for progress in progresses])

		return score

	def get_user_courses(self, user_id):
		page = 1
		while page:
			response = self.__fetch_courses(user_id, page)
			course_list = [
				{
					'stepic_id': course['id'],
					'title': course['title'],
					'summary': course['summary'],
					'cover': 'https://stepik.org{}'.format(course['cover']),
					'cert_reg_threshold': course['certificate_regular_threshold'],
					'cert_dist_threshold': course['certificate_distinction_threshold'],
					'score': self.get_course_score(course)}
				for course in response['courses']]
			page = page + 1 if response['meta']['has_next'] else 0

		return course_list

	def get_course_comments(self, course_id):
		page = 1
		comment_list = []
		while page:
			response = self.__fetch_comments(course_id, page)
			comment_list += [
				{
					'stepic_id': comment['id'],
					'parent_id': comment['parent'],
					'course_id': course_id,
					'step_id': comment['target'],
					'user_id': comment['user'],
					'user_role': comment['user_role'],
					'time': comment['time'],
					'last_time': comment['last_time'],
					'text': comment['text'],
					'replies': comment['replies'],
					'reply_count': comment['reply_count'],
					'is_deleted': comment['is_deleted'],
					'is_pinned': comment['is_pinned'],
					'is_staff_replied': comment['is_staff_replied'],
					'is_reported': comment['is_reported'],
					'attachments': comment['attachments'],
					'epic_count': comment['epic_count'],
					'abuse_count': comment['abuse_count']
				}
				for comment in response['comments']]
			page = page + 1 if response['meta']['has_next'] else 0

		return comment_list

	def get_user_course_grades(self, user_id, course_id):
		return self.__fetch_course_grades(course_id, user_id)[STEPIC_COURSE_GRADES]
