from table_builder.forms import TableSchemaForm
from table_builder.src.entity.db_broker import DBBroker
from table_builder.src.services.to_schema_converters import DjangoModelTableSchemaConverter, SQLAlchemyTableSchemaConverter


class SchemaBuilder:
	def __init__(self, view):
		self.view = view

	def get_schema(self):
		raise NotImplementedError()


class TableModelSchemaBuilder(SchemaBuilder):
	"""
	Стратегия предоставления схемы, полученной из таблицы Table
	"""
	converter = DjangoModelTableSchemaConverter

	def get_object(self):
		if hasattr(self.view, 'object'):
			return self.view.object
		else:
			raise NotImplementedError()

	def get_schema(self):
		obj = self.get_object()
		return self.converter.convert(obj)


class POSTRequestTableSchemaBuilder(SchemaBuilder):
	"""
	Стратегия предоставления схемы из данных POST запроса
	"""
	form = TableSchemaForm

	def get_schema(self):
		form = self.form(self.view.request.POST)
		form.is_valid()
		return form.cleaned_data


class SQLAlchemySchemaBuilder(SchemaBuilder):
	"""
	Стратегия предоставления схемы из отражения внешней таблицы.
	ВНИМАНИЕ!!! Возвращает схемы всех таблиц базы данных
	"""
	def get_object(self):
		if hasattr(self.view, 'object'):
			return self.view.object
		else:
			raise NotImplementedError()

	def get_schema(self):
		database = self.get_object()
		connection_url = database.get_connection_url()
		db_broker = DBBroker(connection_url)
		raw_schema = db_broker.get_schema()
		return (
			SQLAlchemyTableSchemaConverter.convert(instance=instance, db_instance=database)
			for instance in raw_schema
		)
