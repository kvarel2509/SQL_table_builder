from sqlalchemy import create_engine, text, MetaData


class DBBroker:
	"""Отвечает за общение с базой данных"""

	errors = {
		'connection': 'Не удалось подключиться к БД'
	}
	engine_kwargs = {
		'future': True,
		'connect_args': {'connect_timeout': 5}
	}

	def __init__(self, connection_url: str, **kwargs):
		self.connection_url = connection_url
		self.engine_kwargs.update(kwargs)
		self.engine = create_engine(self.connection_url, **self.engine_kwargs)

	def get_schema(self):
		meta = MetaData()
		try:
			meta.reflect(bind=self.engine)
		except Exception:
			raise AttributeError(self.errors['connection'])
		table_list = list(meta.tables.values())
		return table_list

	def run_query(self, query: str, params: dict = None):
		if params is None:
			params = {}
		try:
			with self.engine.connect() as c:
				result = c.execute(text(query), params).all()
		except Exception:
			raise AttributeError(self.errors['connection'])
		return result
