import requests

LOGIN_ENDPOINT = '/login/token.php'
WEBSERVICE_ENDPOINT = '/webservice/rest/server.php'
MOODLE_SERVICE = 'moodle_mobile_app'
PARAM_TOKEN = 'wstoken'
PARAM_FUNCTION = 'wsfunction'
PARAM_FORMAT = 'moodlewsrestformat'


class MoodleAuth:

	def __init__(self, form):
		self.__site_url = form.get('site_url')
		self.__username = form.get('username')
		self.__password = form.get('password')

	def get_site_url(self):
		return self.__site_url

	def get_user_token(self):
		url = self.__site_url + LOGIN_ENDPOINT
		param_dict = {
			'username': self.__username,
			'password': self.__password,
			'service': MOODLE_SERVICE}

		response = requests.get(url, params=param_dict).json()
		print(response)

		return response.get('token')


class MoodleApi:

	def __init__(self, site_url, token):
		self.__site_url = site_url
		self.__token = token

	def __get_site_info(self):
		url = self.__site_url + WEBSERVICE_ENDPOINT
		param_dict = {
			PARAM_TOKEN: self.__token,
			PARAM_FUNCTION: 'core_webservice_get_site_info',
			PARAM_FORMAT: 'json'}

		return requests.get(url, params=param_dict).json()

	def __get_course_content(self):
		url = self.__site_url + WEBSERVICE_ENDPOINT
		param_dict = {
			PARAM_TOKEN: self.__token,
			PARAM_FUNCTION: 'core_course_get_content',
			PARAM_FORMAT: 'json'}

		return requests.get(url, params=param_dict).json()

	# **************************************************************************
	# Public functions
	# **************************************************************************
	def get_current_user_profile(self):
		return self.__get_site_info()
