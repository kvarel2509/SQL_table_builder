from typing import Iterable

from table_builder.src.owns.constants import Message
from table_builder.src.owns.schema import TableSchema


class SQLFormSet:
	def __init__(self, table_schema: TableSchema, forms: Iterable):
		self.table_schema = table_schema
		self.forms = list(forms)
		self._errors = None

	@property
	def errors(self):
		if self._errors is None:
			self.full_clean()
		return self._errors

	def is_valid(self):
		return not self.errors

	def full_clean(self):
		self._errors = {}
		self._clean_forms()
		self._clean_formset()
		self._edit_table_schema()

	def _clean_forms(self):
		for form in self.forms:
			if not form.is_valid():
				self._errors[form.prefix] = [
					f'{field}: {text}'
					for field, errors in form.errors.items()
					for text in errors
				]

	def _clean_formset(self):
		if self.errors:
			return
		if not any([form.instance.show for form in self.forms]):
			self._errors.setdefault('query', list()).append(Message.NO_FIELDS_SELECTED.value)

	def _edit_table_schema(self):
		if self.errors:
			return
		for column_schema, form in zip(self.table_schema, self.forms):
			column_schema.instance = form.instance

	def save(self, commit=True):
		for form in self.forms:
			form.save(commit)
		return self.instances

	@property
	def instances(self):
		for form in self.forms:
			yield form.instance
