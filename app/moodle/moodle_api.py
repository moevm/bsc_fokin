import requests

LOGIN_ENDPOINT = '/login/token.php'
WEBSERVICE_ENDPOINT = '/webservice/rest/server.php'
MOODLE_SERVICE = 'moodle_mobile_app'
COURSE_COVER = '/static/images/moodle_course_cover.jpg'
# ******************************************************************************
PARAM_TOKEN = 'wstoken'
PARAM_FUNCTION = 'wsfunction'
PARAM_FORMAT = 'moodlewsrestformat'
# ******************************************************************************
PARAM_USER_ID = 'userid'
PARAM_COURSE_ID = 'courseid'
PARAM_COURSE_IDS = 'courseids[]'
PARAM_FORUM_ID = 'forumid'
PARAM_DISCUSSION_ID = 'discussionid'


class MoodleAuth:

	def __init__(self, form):
		self.__moodle_url = form.get('moodle_url')
		self.__username = form.get('username')
		self.__password = form.get('password')

	def get_moodle_url(self):
		return self.__moodle_url

	def get_user_token(self):
		url = self.__moodle_url + LOGIN_ENDPOINT
		param_dict = {
			'username': self.__username,
			'password': self.__password,
			'service': MOODLE_SERVICE}

		response = requests.get(url, params=param_dict).json()
		print(response)

		return response.get('token')


class MoodleApi:

	def __init__(self, moodle_url, token):
		self.__moodle_url = moodle_url
		self.__token = token

	def __get_site_info(self):
		url = self.__moodle_url + WEBSERVICE_ENDPOINT
		param_dict = {
			PARAM_TOKEN: self.__token,
			PARAM_FUNCTION: 'core_webservice_get_site_info',
			PARAM_FORMAT: 'json'}

		return requests.get(url, params=param_dict).json()

	def __get_users_courses(self, user_id):
		url = self.__moodle_url + WEBSERVICE_ENDPOINT
		param_dict = {
			PARAM_USER_ID: user_id,
			PARAM_TOKEN: self.__token,
			PARAM_FUNCTION: 'core_enrol_get_users_courses',
			PARAM_FORMAT: 'json'}

		return requests.get(url, params=param_dict).json()

	# course_id should be list, but is's int
	def __get_forums_by_courses(self, course_id):
		url = self.__moodle_url + WEBSERVICE_ENDPOINT
		param_dict = {
			PARAM_COURSE_IDS: course_id,
			PARAM_TOKEN: self.__token,
			PARAM_FUNCTION: 'mod_forum_get_forums_by_courses',
			PARAM_FORMAT: 'json'}

		return requests.get(url, params=param_dict).json()

	def __get_forum_discussions(self, forum_id):
		url = self.__moodle_url + WEBSERVICE_ENDPOINT
		param_dict = {
			PARAM_FORUM_ID: forum_id,
			PARAM_TOKEN: self.__token,
			PARAM_FUNCTION: 'mod_forum_get_forum_discussions',
			PARAM_FORMAT: 'json'}

		return requests.get(url, params=param_dict).json()

	def __get_discussion_posts(self, discussion_id):
		url = self.__moodle_url + WEBSERVICE_ENDPOINT
		param_dict = {
			PARAM_DISCUSSION_ID: discussion_id,
			PARAM_TOKEN: self.__token,
			PARAM_FUNCTION: 'mod_forum_get_discussion_posts',
			PARAM_FORMAT: 'json'}

		return requests.get(url, params=param_dict).json()

	def __get_user_course_gradereport(self, course_id, user_id):
		url = self.__moodle_url + WEBSERVICE_ENDPOINT
		param_dict = {
			PARAM_COURSE_ID: course_id,
			PARAM_USER_ID: user_id,
			PARAM_TOKEN: self.__token,
			PARAM_FUNCTION: 'gradereport_user_get_grade_items',
			PARAM_FORMAT: 'json'}

		return requests.get(url, params=param_dict).json()

	# **************************************************************************
	# Public functions
	# **************************************************************************
	def get_current_user_profile(self):
		return self.__get_site_info()

	def get_user_courses(self, user_id):
		course_list = self.__get_users_courses(user_id)
		course_list = [
			{
				'moodle_id': course.get('id'),
				'short_name': course.get('shortname'),
				'full_name': course.get('fullname'),
				'display_name': course.get('displayname'),
				'summary': course.get('summary'),
				'enrolled_user_count': course.get('enrolledusercount'),
				'visible': True if course.get('visible') == 1 else False,
				'format': course.get('format'),
				'show_grades': course.get('showgrades'),
				'start_date': course.get('startdate'),
				'cover': course.get('overviewfiles')[0].get('fileurl').replace('/webservice', '') if course.get('overviewfiles') else COURSE_COVER}
			for course in course_list]

		return course_list

	def get_course_forums(self, course_id):
		forum_list = self.__get_forums_by_courses(course_id)
		forum_list = [
			{
				'moodle_id': forum.get('id'),
				'type': forum.get('type'),
				'name': forum.get('name'),
				'intro': forum.get('intro'),
				'scale': forum.get('scale')}
			for forum in forum_list]

		return forum_list

	def get_forum_discussions(self, forum_id):
		forum_discussions = self.__get_forum_discussions(forum_id)
		discussion_list = forum_discussions.get('discussions') if forum_discussions.get('discussions') else []
		discussion_list = [
			{
				'moodle_id': discussion.get('id'),
				'discussion_id': discussion.get('discussion'),
				'name': discussion.get('name'),
				'subject': discussion.get('subject'),
				'message': discussion.get('message'),
				'created': discussion.get('created'),
				'user_id': discussion.get('userid'),
				'user_full_name': discussion.get('userfullname'),
				'user_picture_url': discussion.get('userpictureurl'),
				'time_modified': discussion.get('timemodified'),
				'user_modified': discussion.get('usermodified'),
				'num_replies': discussion.get('numreplies')}
			for discussion in discussion_list]

		return discussion_list

	def get_discussion_posts(self, discussion_id):
		discussion_posts = self.__get_discussion_posts(discussion_id)
		post_list = discussion_posts.get('posts') if discussion_posts.get('posts') else []
		post_list = [
			{
				'moodle_id': post.get('id'),
				'subject': post.get('subject'),
				'reply_subject': post.get('replysubject'),
				'message': post.get('message'),
				'user_id': post.get('author').get('id'),
				'user_full_name': post.get('author').get('fullname'),
				'user_url': post.get('author').get('urls').get('profile'),
				'user_picture_url': post.get('author').get('urls').get('profileimage'),
				'has_parent': post.get('hasparent'),
				'parent_id': post.get('parentid'),
				'time_created': post.get('timecreated'),
				'tags': post.get('tags'),
				'rating': next((rating for rating in discussion_posts.get('ratinginfo').get('ratings') if rating.get('itemid') == post.get('id')), {})}
			for post in post_list]

		return post_list

	def get_user_course_grade(self, course_id, user_id):
		user_course_grades = self.__get_user_course_gradereport(course_id, user_id)
		if user_course_grades.get('exception'):
			return {'exception': user_course_grades.get('message')}

		for grade_item in user_course_grades.get('usergrades')[0].get('gradeitems'):
			if grade_item.get('itemtype') == 'course':
				user_course_grade = {
					'course_grade': grade_item.get('grademax'),
					'user_grade': {
						str(course_id): grade_item.get('graderaw') if grade_item.get('graderaw') != None else 0
					}
				}
				break

		return user_course_grade
