from table_builder.src.owns.constants import (
	OrderChoice,
	StringWhereChoice,
	NumberWhereChoice,
	ColumnType
)
from table_builder.src.owns.schema import TableSchema, ColumnSchema


class QueryParams:
	PREFIX = 'var_'

	def __init__(self):
		self.params = dict()
		self._counter = 0

	def add_param(self, value):
		var = self.next_var()
		self.params[var] = value
		return var

	def next_var(self):
		var = f'{self.PREFIX}{str(self._counter)}'
		self._counter += 1
		return var


class SQLQueryBuilder:
	def __init__(self, table_schema: TableSchema):
		self.table_schema = table_schema

	@property
	def table_schema(self):
		return self._table_schema

	@table_schema.setter
	def table_schema(self, value: TableSchema):
		self._table_schema = value
		self.query_param = QueryParams()
		self.query = None

	def build_sql_query(self):
		if not self.query:
			select_section = self.build_select_section()
			from_section = self.build_from_section()
			where_section = self.build_where_section()
			order_section = self.build_order_section()
			self.query = ' '.join(filter(bool, [select_section, from_section, where_section, order_section]))
		return self.query, self.query_param.params

	def build_select_section(self):
		columns = []
		for column in self.table_schema:
			if column.instance.show:
				s = column.name
				if column.instance.alias:
					s += f' as "{column.instance.alias}"'
				columns.append(s)
		return f'SELECT {", ".join(columns)}'

	def build_from_section(self):
		return f'FROM {self.table_schema.name}'

	def build_where_section(self):
		where_condition_builder_matching = {
			ColumnType.INTEGER.value: NumberWhereConditionBuilder,
			ColumnType.FLOAT.value: NumberWhereConditionBuilder,
			ColumnType.CHAR.value: StringWhereConditionBuilder,
			ColumnType.DATE.value: DateWhereConditionBuilder,
			ColumnType.DATETIME.value: DateWhereConditionBuilder,
			ColumnType.DURATION.value: DateWhereConditionBuilder
		}
		conditions = []
		for column in self.table_schema:
			column_type = column.data_type
			condition = where_condition_builder_matching[column_type](self, column).build_condition()
			if condition:
				conditions.append(condition)
		return f'WHERE {" AND ".join(conditions)}' if conditions else ''

	def build_order_section(self):
		columns = [
			column
			for column in self.table_schema
			if column.instance.order_predicate != OrderChoice.NOT.value
		]
		columns.sort(key=lambda x: x.instance.order_priority, reverse=True)
		columns = [
			f'{column.name} {column.instance.order_predicate}'
			for column in columns
		]
		return f'ORDER BY {", ".join(columns)}' if columns else ''


class StringWhereConditionBuilder:
	def __init__(self, builder: SQLQueryBuilder, column: ColumnSchema):
		self.builder = builder
		self.column = column

	def build_condition(self):
		t = ''
		instance = self.column.instance
		if instance.where_predicate == StringWhereChoice.NOT.value:
			return t
		if instance.where_not:
			t += 'NOT '
		t += f'{instance.name} '
		if instance.where_predicate == StringWhereChoice.EQ.value:
			t += f'= :{self.builder.query_param.add_param(instance.where_value)}'
		elif instance.where_predicate == StringWhereChoice.CONTAINS.value:
			t += f'LIKE :{self.builder.query_param.add_param("%" + instance.where_value + "%")}'
		elif instance.where_predicate == StringWhereChoice.STARTSWITH.value:
			t += f'LIKE :{self.builder.query_param.add_param(instance.where_value + "%")}'
		elif instance.where_predicate == StringWhereChoice.ENDSWITH.value:
			t += f'LIKE :{self.builder.query_param.add_param("%" + instance.where_value)}'

		return t


class NumberWhereConditionBuilder:
	def __init__(self, builder: SQLQueryBuilder, column: ColumnSchema):
		self.builder = builder
		self.column = column

	def build_condition(self):
		t = ''
		instance = self.column.instance
		if instance.where_predicate == NumberWhereChoice.NOT.value:
			return t
		if instance.where_not:
			t += 'NOT '
		t += f'{instance.name} '
		if instance.where_predicate == NumberWhereChoice.EQ.value:
			t += f'= :{self.builder.query_param.add_param(instance.where_value)}'
		elif instance.where_predicate == NumberWhereChoice.GT.value:
			t += f'> :{self.builder.query_param.add_param(instance.where_value)}'
		elif instance.where_predicate == NumberWhereChoice.LT.value:
			t += f'< :{self.builder.query_param.add_param(instance.where_value)}'

		return t


class DateWhereConditionBuilder:
	def __init__(self, builder: SQLQueryBuilder, column: ColumnSchema):
		self.builder = builder
		self.column = column

	def build_condition(self):
		column_name = self.column.name
		t = ''
		instance = self.column.instance
		if not instance.where_from_value and not instance.where_to_value:
			return t
		if instance.where_not:
			t += 'NOT '
		t += f'{column_name} '
		if instance.where_from_value and instance.where_to_value:
			t += f'BETWEEN '
			t += f':{self.builder.query_param.add_param(instance.where_from_value)} '
			t += 'AND '
			t += f':{self.builder.query_param.add_param(instance.where_to_value)}'
		elif instance.where_from_value:
			t += f'>= :{self.builder.query_param.add_param(instance.where_from_value)} '
		elif instance.where_to_value:
			t += f'<= :{self.builder.query_param.add_param(instance.where_to_value)} '

		return t
