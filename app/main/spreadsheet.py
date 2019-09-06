import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config.config_reader as cr


class GSpread:

	def __init__(self, spreadsheet_key):
		self.__scope__ = [
			'https://spreadsheets.google.com/feeds',
			'https://www.googleapis.com/auth/drive']
		self.__credentials_path__ = cr.get_gspread_credentials_path()
		self.__spreadsheet_key__ = spreadsheet_key
		self.__gclient__ = self.__get_client__()

	def __get_client__(self):
		credentials = ServiceAccountCredentials.from_json_keyfile_name(
			self.__credentials_path__,
			self.__scope__)
		gclient = gspread.authorize(credentials)

		return gclient

	def __get_students__(self, worksheet):
		student_list = worksheet.get_all_values()[1:]

		return student_list

	def get_groups(self):
		spreadsheet = self.__gclient__.open_by_key(self.__spreadsheet_key__)
		worksheet_list = spreadsheet.worksheets()
		group_dict = {worksheet.title: self.__get_students__(worksheet) for worksheet in worksheet_list}

		return group_dict
