from datetime import date, datetime
from app.create_app import db


class FiltrationSet(db.Document):
	serial_id = db.SequenceField()
	# название фильтра
	title = db.StringField(default='', unique=True)
	# поле "Дата"
	date_from = db.IntField(default=0)
	date_to = db.IntField(default=0)
	date_order = db.StringField(default='-')
	# поле "Ответы"
	replies_from = db.IntField(default=0)
	replies_to = db.IntField(default=10)
	replies_order = db.StringField(default='-')
	# поле "Прогресс"
	progress_from = db.IntField(default=0)
	progress_to = db.IntField(default=100)
	progress_order = db.StringField(default='-')
	# разрешено наследование
	meta = {'allow_inheritance': True}

	def get_info(self):
		return self.to_json()

	# url параметры поля "Дата"
	def get_date_args_url(self):
		date_args_url = 'date[from]={}&date[to]={}&date[order]={}'.format(
			date.fromtimestamp(self.date_from).isoformat(),
			date.fromtimestamp(self.date_to).isoformat(),
			self.date_order)

		return date_args_url

	# url параметры поля "Ответы"
	def get_replies_args_url(self):
		replies_args_url = 'replies[from]={}&replies[to]={}&replies[order]={}'.format(
			self.replies_from,
			self.replies_to,
			self.replies_order)

		return replies_args_url

	# url параметры поля "Прогресс"
	def get_progress_args_url(self):
		progress_args_url = 'progress[from]={}&progress[to]={}&progress[order]={}'.format(
			self.progress_from,
			self.progress_to,
			self.progress_order)

		return progress_args_url
