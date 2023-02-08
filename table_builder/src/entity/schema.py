from typing import Sequence


class ColumnSchema:
	def __init__(self, *, name, data_type, pk=None, instance=None):
		self.name = name
		self.data_type = data_type
		self.instance = instance
		self.pk = pk
		if instance is not None:
			self.pk = instance.pk

	def __eq__(self, other):
		if type(other) == self.__class__:
			return self.name == other.name and self.data_type == other.data_type
		else:
			raise NotImplementedError()

	def __hash__(self):
		return hash((self.name, self.data_type))


class TableSchema:
	def __init__(
		self, *, name, pk=None, column_schemes: Sequence[ColumnSchema] = None,
		instance=None, db_pk=None, db_instance=None
	):
		self.name = name
		self.column_schemes = list(column_schemes)
		self.instance = instance
		self.pk = pk
		self.db_pk = db_pk
		self.db_instance = db_instance
		if instance is not None:
			self.pk = instance.pk
		if db_instance is not None:
			self.db_pk = db_instance.pk

	def __iter__(self):
		return (column_schema for column_schema in self.column_schemes)
