from django.db.models import TextChoices


class OrderChoice(TextChoices):
	NOT = '', '---'
	ASC = 'ASC', 'По возрастанию'
	DESC = 'DESC', 'По убыванию'


class NumberWhereChoice(TextChoices):
	NOT = '', '---'
	EQ = '=', 'Равно'
	GT = '>', 'Больше'
	LT = '<', 'Меньше'


class StringWhereChoice(TextChoices):
	NOT = '', '---'
	EQ = '=', 'Равно'
	CONTAINS = '%LIKE%', 'Содержит'
	STARTSWITH = 'LIKE%', 'Начинается'
	ENDSWITH = '%LIKE', 'Заканчивается'


class ColumnType(TextChoices):
	INTEGER = 'int', 'INTEGER'
	FLOAT = 'float', 'FLOAT'
	CHAR = 'str', 'STRING'
	DATE = 'date', 'DATE'
	DATETIME = 'datetime', 'DATETIME'
	DURATION = 'duration', 'DURATION'


class DialectDB(TextChoices):
	POSTGRES = 'postgresql', 'PostgreSQL'


class SQLParam(TextChoices):
	SHOW = 'show', 'Показать'
	ALIAS = 'alias', 'Псевдоним'
	WHERE = 'where', 'Фильтрация'
	ORDER = 'order', 'Сортировка'


class WhereSQLParam(TextChoices):
	NOT = 'not', 'Не'
	PREDICATE = 'predicate', 'Условие'
	VALUE = 'value', 'Значение'


class RangeSQLParam(TextChoices):
	FROM = 'from', 'От'
	TO = 'to', 'До'


class OrderSQLParam(TextChoices):
	PREDICATE = 'predicate', 'Условие'
	PRIORITY = 'priority', 'Приоритет'


class SchemaNotation(TextChoices):
	DB = 'db'
	TABLE = 'instance'
	COLUMNS = 'columns'
	COLUMN_NAME = 'column_name'
	COLUMN_TYPE = 'column_type'
	SCHEMA_FIELD_NAME = 'schema'


class Message(TextChoices):
	NOT_CONNECTION_DB = 'Нет подключения к БД'
	INVALID_SQL_QUERY = 'Некорректный запрос'
	NO_FIELDS_SELECTED = 'Не выбраны поля для отображения'
	SUCCESS_UPDATE_SCHEMA = 'Схема успешна обновлена'
	SUCCESS_CREATE_SCHEMA = 'Схема успешна сохранена'


class TemplateName(TextChoices):
	SQL_PARAMS_FORMS = 'sql_params_forms'
	TABLE_FORM = 'table_form'
	SCHEMA_FORM = 'schema_form'
	DB = 'db'
	LOCAL_TABLES = 'local_schemes'
	AUTO_TABLES = 'auto_schemes'
