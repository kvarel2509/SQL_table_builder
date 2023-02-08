from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from rest_framework import views, response
from rest_framework_csv import renderers

from table_builder import forms
from table_builder import models
from table_builder.src.generics.renderers import OrderDictCSVRender
from table_builder.src.entity.constants import Message, TemplateName
from table_builder.src.entity.db_broker import DBBroker
from table_builder.src.services.form_builders import (
	FieldFormsWithInstanceBuilder,
	FieldFormsWithoutInstanceBuilder,
	FieldFormsWithFillTemplateBuilder,
	BaseSchemaFormBuilder,
	SchemaChoicesFormBuilder
)
from table_builder.src.services.mixins import SQLParamsMixin, TableDetailMixin
from table_builder.src.services.query_constructor import SQLQueryBuilder
from table_builder.src.services.schema_builder import (
	POSTRequestTableSchemaBuilder,
	TableModelSchemaBuilder,
	SQLAlchemySchemaBuilder
)
from table_builder.src.services.sql_formset import SQLFormSet


class DatabaseListView(generic.ListView):
	model = models.Database
	template_name = 'tablebuilder/database_list.html'


class DatabaseDetailView(SQLParamsMixin, generic.DetailView):
	schema_build_strategy = SQLAlchemySchemaBuilder
	schema_form_builder = SchemaChoicesFormBuilder
	model = models.Database
	template_name = 'tablebuilder/database_detail.html'

	def get(self, request, *args, **kwargs):
		try:
			return super().get(request, *args, **kwargs)
		except AttributeError:
			messages.error(request=self.request, message=Message.NOT_CONNECTION_DB.value)
			return HttpResponseRedirect(redirect_to=reverse_lazy('database_list'))

	def get_local_tables(self):
		return self.object.tables.all()

	def get_context_data(self, **kwargs):
		ctx = dict()
		ctx[TemplateName.LOCAL_TABLES.value] = self.get_local_tables()
		ctx[TemplateName.AUTO_TABLES.value] = self.schema_form
		return super().get_context_data(**ctx, **kwargs)


class AutoSchemaTableDetail(TableDetailMixin, generic.TemplateView):
	schema_build_strategy = POSTRequestTableSchemaBuilder
	field_forms_builder = FieldFormsWithFillTemplateBuilder
	schema_form_builder = BaseSchemaFormBuilder
	template_name = 'tablebuilder/auto_table.html'

	def post(self, request, *args, **kwargs):
		return super().get(request, *args, **kwargs)

	def get_table_form(self):
		table_name = self.schema.name
		database_id = self.schema.db_pk
		return forms.TableForm(initial={'name': table_name, 'database': database_id})


class LocalSchemaTableDetail(TableDetailMixin, generic.DetailView):
	schema_build_strategy = TableModelSchemaBuilder
	field_forms_builder = FieldFormsWithInstanceBuilder
	schema_form_builder = BaseSchemaFormBuilder
	model = models.Table
	template_name = 'tablebuilder/local_table.html'

	def get_table_form(self):
		return forms.TableForm(instance=self.object)


class DataRequestAPIView(generic.detail.SingleObjectMixin, SQLParamsMixin, views.APIView):
	schema_build_strategy = POSTRequestTableSchemaBuilder
	field_forms_builder = FieldFormsWithoutInstanceBuilder
	model = models.Database
	renderer_classes = [renderers.JSONRenderer, OrderDictCSVRender]

	def post(self, request, *args, **kwargs):
		data = self.get_data()
		headers = {}
		if isinstance(self.request.accepted_renderer, OrderDictCSVRender):
			headers.update(OrderDictCSVRender.get_headers())
		return response.Response(data=data, headers=headers)

	def get_field_forms_kwargs(self):
		kwargs = super().get_field_forms_kwargs()
		kwargs.update({'data': self.request.data})
		return kwargs

	def get_data(self):
		formset = SQLFormSet(self.schema, self.field_forms)
		if not formset.is_valid():
			return [formset.errors]
		database = self.get_object()
		connection_url = database.get_connection_url()
		db_broker = DBBroker(connection_url)
		query, params = SQLQueryBuilder(formset.table_schema).build_sql_query()
		try:
			data = db_broker.run_query(query, params)
			return [dict(row) for row in data]
		except AttributeError:
			return [{'db': Message.NOT_CONNECTION_DB.value}]


class UpdateSchemaView(generic.detail.SingleObjectMixin, SQLParamsMixin, views.APIView):
	schema_build_strategy = POSTRequestTableSchemaBuilder
	field_forms_builder = FieldFormsWithInstanceBuilder
	model = models.Table

	def post(self, request, *args, **kwargs):
		self.update_table()
		self.update_columns()
		return response.Response([{Message.SUCCESS_UPDATE_SCHEMA.value: ''}])

	def update_table(self):
		table_obj = self.get_object()
		form = forms.TableForm(data=self.request.POST, instance=table_obj)
		form.is_valid()
		return form.save()

	def update_columns(self):
		formset = SQLFormSet(self.schema, self.field_forms)
		formset.is_valid()
		formset.save()

	def get_field_forms_kwargs(self):
		kwargs = super().get_field_forms_kwargs()
		kwargs.update({'data': self.request.data})
		return kwargs


class CreateSchemaView(SQLParamsMixin, generic.RedirectView):
	schema_build_strategy = POSTRequestTableSchemaBuilder
	field_forms_builder = FieldFormsWithoutInstanceBuilder

	def post(self, request, *args, **kwargs):
		self.table_obj = self.create_table()
		self.create_columns()
		messages.success(request=request, message=Message.SUCCESS_CREATE_SCHEMA.value)
		return super().post(request, *args, **kwargs)

	def create_table(self):
		form = forms.TableForm(data=self.request.POST)
		form.is_valid()
		return form.save()

	def create_columns(self):
		formset = SQLFormSet(self.schema, self.field_forms)
		for instance in formset.instances:
			instance.column_set = self.table_obj
		formset.save()

	def get_field_forms_kwargs(self):
		kwargs = super().get_field_forms_kwargs()
		kwargs.update({'data': self.request.POST})
		return kwargs

	def get_redirect_url(self, *args, **kwargs):
		return reverse_lazy('local_schema_detail', kwargs={'pk': self.table_obj.pk})


class DeleteSchemaView(generic.detail.SingleObjectMixin, generic.edit.DeletionMixin, generic.View):
	model = models.Table

	def get(self, *args, **kwargs):
		return super().post(*args, **kwargs)

	def get_success_url(self):
		return reverse_lazy('database_detail', kwargs={'pk': self.object.database_id})
