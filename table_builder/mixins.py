from typing import Type

from django.utils.functional import cached_property

from table_builder.src.entity.constants import TemplateName
from table_builder.src.interface.form_builders import SQLFormBuilder
from table_builder.src.interface.schema_builder import SchemaBuilder


class SQLParamsMixin:
	schema_form_builder: Type[SQLFormBuilder]
	field_forms_builder: Type[SQLFormBuilder]
	schema_build_strategy: Type[SchemaBuilder]

	def get_field_forms_kwargs(self) -> dict:
		return dict()

	def get_schema_forms_kwargs(self) -> dict:
		return dict()

	@cached_property
	def schema(self):
		return self.schema_build_strategy(self).get_schema()

	@cached_property
	def field_forms(self):
		form_builder = self.field_forms_builder(self.schema)
		kwargs = self.get_field_forms_kwargs()
		return list(form_builder.get_form(**kwargs))

	@cached_property
	def schema_form(self):
		form_builder = self.schema_form_builder(self.schema)
		kwargs = self.get_schema_forms_kwargs()
		return form_builder.get_form(**kwargs)


class TableDetailMixin(SQLParamsMixin):
	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx[TemplateName.SQL_PARAMS_FORMS.value] = self.field_forms
		ctx[TemplateName.SCHEMA_FORM.value] = self.schema_form
		ctx[TemplateName.DB.value] = self.schema.db_pk
		ctx[TemplateName.TABLE_FORM.value] = self.get_table_form()
		return ctx

	def get_table_form(self):
		raise NotImplementedError()
