from typing import Generator

from table_builder import forms, models
from table_builder.models import Table
from table_builder.src.entity.constants import ColumnType
from table_builder.src.entity.schema import TableSchema
from table_builder.src.services.to_schema_converters import DjangoModelAutoFillTemplateSchemaConverter


class SQLFormBuilder:
	"""Базовый класс для создания форм на базе шаблонного метода"""

	def __init__(self, table_schema: TableSchema):
		self.table_schema = table_schema

	def get_form(self, **kwargs):
		raise NotImplementedError()


class BaseSchemaFormBuilder(SQLFormBuilder):
	"""Формирует форму со схемой таблицы"""
	form = forms.TableSchemaForm

	def get_form(self, **kwargs):
		return self.form(table_schema=self.table_schema, **kwargs)


class SchemaChoicesFormBuilder:
	"""Формирует форму со списком схем"""
	form = forms.AutoSchemaChoicesForm
	
	def __init__(self, table_schemes):
		self.table_schemes = table_schemes

	def get_form(self, **kwargs):
		return self.form(table_schemes=self.table_schemes, **kwargs)


class SQLFieldsMatch:
	match = {
		ColumnType.INTEGER.value: forms.IntegerColumnForm,
		ColumnType.CHAR.value: forms.CharColumnForm,
		ColumnType.FLOAT.value: forms.FloatColumnForm,
		ColumnType.DATE.value: forms.DateColumnForm,
		ColumnType.DATETIME.value: forms.DateTimeColumnForm,
		ColumnType.DURATION.value: forms.DurationColumnForm,
	}


class FieldFormsWithInstanceBuilder(SQLFieldsMatch, SQLFormBuilder):
	"""Стратегия для составления формы, где требуется наличие instance столбца"""

	def get_form(self, **kwargs) -> Generator:
		if self.table_schema.instance is not None:
			for column_schema in self.table_schema:
				instance = column_schema.instance
				if instance is None:
					raise ValueError('Схема реализована не корректно')
				form = self.match[column_schema.data_type]
				yield form(instance=instance, prefix=instance.name, **kwargs)

		elif self.table_schema.pk is not None:
			instances = self._get_instances()
			for column_schema in self.table_schema:
				form = self.match[column_schema.data_type]
				instance = next(instances)
				yield form(instance=instance, prefix=instance.name, **kwargs)

		else:
			raise ValueError('Невозможно получить instance')

	def _get_instances(self) -> Generator:
		table_instance = Table.objects.get(pk=self.table_schema.pk)
		return table_instance.get_columns()


class FieldFormsWithoutInstanceBuilder(SQLFieldsMatch, SQLFormBuilder):
	"""Стратегия для составления формы, где не требуется instance, например, когда используется авто-схема"""

	def get_form(self, **kwargs) -> Generator:
		gen_form_kwargs = self._get_form_kwargs(**kwargs)
		next(gen_form_kwargs)
		for column_schema in self.table_schema:
			form_kwargs = gen_form_kwargs.send(column_schema)
			form = self.match[column_schema.data_type]
			yield form(**form_kwargs)

	def _get_form_kwargs(self, **kwargs):
		counter = 1
		while True:
			column_schema = yield kwargs
			kwargs.setdefault('initial', dict()).update({
				'name': column_schema.name,
				'position': counter
			})
			kwargs['prefix'] = column_schema.name
			counter += 1


class FieldFormsWithFillTemplateBuilder(SQLFieldsMatch, SQLFormBuilder):
	"""Стратегия подменяет базовую схему столбца аналогичной схемой из набора правил, если он существует"""

	def get_form(self, **kwargs) -> Generator:
		template_schema = self._get_template_schema()
		if template_schema:
			merged_schemes = self._get_merged_column_schemes(template_schema)
		else:
			merged_schemes = self.table_schema
		gen_form_kwargs = self._get_form_kwargs(**kwargs)
		next(gen_form_kwargs)
		for column_schema in merged_schemes:
			form_kwargs = gen_form_kwargs.send(column_schema)
			form = self.match[column_schema.data_type]
			yield form(**form_kwargs)

	def _get_form_kwargs(self, **init_kwargs):
		counter = 1
		kwargs = None
		while True:
			column_schema = yield kwargs
			kwargs = dict(**init_kwargs)
			name = column_schema.name
			instance = column_schema.instance
			if instance is None:
				kwargs.setdefault('initial', dict()).update({
					'name': name,
					'position': counter
				})
			else:
				instance.position = counter
				kwargs['instance'] = instance
			kwargs['prefix'] = name
			counter += 1

	def _get_merged_column_schemes(self, template_schema: TableSchema):
		merging_dict = {column_schema: column_schema for column_schema in self.table_schema}
		for column_schema in template_schema:
			if column_schema in merging_dict:
				merging_dict[column_schema] = column_schema
		return list(merging_dict.values())

	def _get_template_schema(self):
		if self.table_schema.db_instance is None:
			self.table_schema.db_instance = models.Database.objects.get(pk=self.table_schema.db_pk)
		auto_fill_template = self.table_schema.db_instance.auto_fill_template
		if auto_fill_template is not None:
			return DjangoModelAutoFillTemplateSchemaConverter.convert(auto_fill_template)
