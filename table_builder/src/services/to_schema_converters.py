import sqlalchemy
from sqlalchemy.dialects.postgresql import base as postgresql_types

from table_builder import models
from table_builder.src.owns.constants import ColumnType, DialectDB
from table_builder.src.owns.schema import TableSchema, ColumnSchema


class DjangoModelColumnSchemaConverter:
	fields_matching = {
		models.DurationColumn: ColumnType.DURATION.value,
		models.DateColumn: ColumnType.DATE.value,
		models.DateTimeColumn: ColumnType.DATETIME.value,
		models.CharColumn: ColumnType.CHAR.value,
		models.FloatColumn: ColumnType.FLOAT.value,
		models.IntegerColumn: ColumnType.INTEGER.value,
	}

	@classmethod
	def convert(cls, instance):
		try:
			column_type = cls.fields_matching[type(instance)]
		except KeyError:
			raise NotImplementedError('Неподдерживаемый тип поля')
		return ColumnSchema(name=instance.name, data_type=column_type, instance=instance)


class DjangoModelTableSchemaConverter:
	column_converter = DjangoModelColumnSchemaConverter

	@classmethod
	def convert(cls, instance: models.Table):
		return TableSchema(
			name=instance.name,
			db_instance=instance.database,
			column_schemes=[cls.column_converter.convert(column) for column in instance.get_columns()],
			instance=instance
		)


class DjangoModelAutoFillTemplateSchemaConverter:
	column_converter = DjangoModelColumnSchemaConverter

	@classmethod
	def convert(cls, instance: models.AutoFillTemplate):
		return TableSchema(
			name=instance.name,
			column_schemes=[cls.column_converter.convert(column) for column in instance.get_columns()],
			instance=instance
		)


class SQLAlchemyColumnSchemaConverter:
	"""
	Базовый класс для сопоставления типов полей внешней БД с типами полей ПО.
	Подклассы должны предоставить атрибут fields_matching
	"""
	fields_matching = {}

	@classmethod
	def convert(cls, instance: sqlalchemy.Column):
		try:
			column_type = cls.fields_matching[type(instance.type)]
		except KeyError:
			raise NotImplementedError('Неподдерживаемый тип поля')
		return ColumnSchema(name=instance.name, data_type=column_type)


class PostgreSQLColumnSchemaConverter(SQLAlchemyColumnSchemaConverter):
	fields_matching = {
		postgresql_types.VARCHAR: ColumnType.CHAR.value,
		postgresql_types.CHAR: ColumnType.CHAR.value,
		postgresql_types.INTEGER: ColumnType.INTEGER.value,
		postgresql_types.FLOAT: ColumnType.FLOAT.value,
		postgresql_types.DATE: ColumnType.DATE.value,
		postgresql_types.TIMESTAMP: ColumnType.DATETIME.value,
	}


class ColumnSchemaConverterFactory:
	"""
	Фабрика конвертеров. В зависимости от диалекта текущей БД ищет подходящий конвертер типов полей.
	"""
	convertors_matching = {
		DialectDB.POSTGRES.value: PostgreSQLColumnSchemaConverter,
	}

	def get_column_schema_converter(self, dialect):
		try:
			return self.convertors_matching[dialect]
		except KeyError:
			raise NotImplementedError('Данный диалект не поддерживается')


class SQLAlchemyTableSchemaConverter:
	column_schema_converter_factory = ColumnSchemaConverterFactory()

	@classmethod
	def convert(cls, instance: sqlalchemy.Table, db_instance: models.Database):
		column_schema_converter = cls.column_schema_converter_factory.get_column_schema_converter(db_instance.dialect)

		return TableSchema(
			name=instance.name,
			db_instance=db_instance,
			column_schemes=[column_schema_converter.convert(column) for column in instance.columns.values()]
		)
