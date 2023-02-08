from typing import Generator

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from table_builder.src.entity.constants import DialectDB
from table_builder.src.entity.abstract_models import (
	Column,
	AliasSection,
	ShowSection,
	OrderSection,
	CharStringWhereSection,
	DateTimeWhereSection,
	DateWhereSection,
	DurationWhereSection,
	IntegerNumberWhereSection,
	FloatNumberWhereSection, ColumnRelation,
)


class FieldRegistry:
	fields = []

	def __new__(cls, *args, **kwargs):
		raise PermissionError('Запрещено создавать экземпляры данного класса')

	@classmethod
	def add_field(cls, field):
		cls.fields.append(field)

	@classmethod
	def register(cls, field_class):
		cls.add_field(field=field_class)
		return field_class


class ColumnRelationMixin:
	def _get_registry(self):
		return FieldRegistry.fields

	def get_columns(self) -> Generator:
		instances = []
		content_type = ContentType.objects.get_for_model(self)
		for field in self._get_registry():
			columns = field.objects.filter(content_type=content_type, object_id=self.pk)
			instances.extend(list(columns)),
		sorted_instances = sorted(instances, key=lambda x: (x.position, x.name))
		for instance in sorted_instances:
			yield instance


class AutoFillTemplate(ColumnRelationMixin, models.Model):
	name = models.CharField(
		verbose_name=_('имя'),
		max_length=255
	)
	description = models.CharField(
		verbose_name=_('описание'),
		max_length=255,
		blank=True
	)

	class Meta:
		verbose_name = _('шаблон автозаполнения')
		verbose_name_plural = _('шаблоны автозаполнения')

	def __str__(self):
		return self.name


class Database(models.Model):
	dialect = models.CharField(
		verbose_name=_('диалект'),
		choices=DialectDB.choices,
		max_length=255
	)
	user = models.CharField(
		verbose_name=_('имя пользователя'),
		max_length=255,
		blank=True
	)
	password = models.CharField(
		verbose_name=_('пароль'),
		max_length=128,
		blank=True
	)
	host = models.CharField(
		verbose_name=_('хост'),
		max_length=255,
		blank=True
	)
	port = models.PositiveIntegerField(
		verbose_name=_('порт'),
		null=True,
		blank=True
	)
	dbname = models.CharField(
		verbose_name=_('название БД'),
		max_length=255
	)
	alias = models.CharField(
		verbose_name=_('псевдоним'),
		max_length=255
	)
	auto_fill_template = models.ForeignKey(
		verbose_name=_('шаблон автозаполнения'),
		to=AutoFillTemplate,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
	)

	class Meta:
		verbose_name = _('база данных')
		verbose_name_plural = _('базы данных')

	def get_connection_url(self):
		params = {}
		for attr in ['user', 'password', 'host', 'port']:
			value = getattr(self, attr)
			if value:
				params[attr] = value

		params_as_str = '&'.join([f'{key}={value}' for key, value in params.items()])
		return f"{self.dialect}:///{self.dbname}?{params_as_str}"

	def __str__(self):
		return self.alias


class Table(ColumnRelationMixin, models.Model):
	name = models.CharField(
		verbose_name=_('название таблицы'),
		max_length=255
	)
	alias = models.CharField(
		verbose_name=_('псевдоним'),
		max_length=255,
		blank=True,
	)
	database = models.ForeignKey(
		verbose_name=_('база данных'),
		to=Database,
		on_delete=models.CASCADE,
		related_name='tables'
	)

	class Meta:
		verbose_name = _('таблица')
		verbose_name_plural = _('таблицы')

	def __str__(self):
		return self.alias

	def get_absolute_url(self):
		return reverse('local_schema_detail', kwargs={'pk': self.pk})


@FieldRegistry.register
class IntegerColumn(Column, ColumnRelation, ShowSection, AliasSection, IntegerNumberWhereSection, OrderSection):

	class Meta:
		verbose_name = _('integer')


@FieldRegistry.register
class FloatColumn(Column, ColumnRelation, ShowSection, AliasSection, FloatNumberWhereSection, OrderSection):

	class Meta:
		verbose_name = _('float')


@FieldRegistry.register
class CharColumn(Column, ColumnRelation, ShowSection, AliasSection, CharStringWhereSection, OrderSection):

	class Meta:
		verbose_name = _('char')


@FieldRegistry.register
class DateColumn(Column, ColumnRelation, ShowSection, AliasSection, DateWhereSection, OrderSection):

	class Meta:
		verbose_name = _('date')


@FieldRegistry.register
class DateTimeColumn(Column, ColumnRelation, ShowSection, AliasSection, DateTimeWhereSection, OrderSection):

	class Meta:
		verbose_name = _('datetime')


@FieldRegistry.register
class DurationColumn(Column, ColumnRelation, ShowSection, AliasSection, DurationWhereSection, OrderSection):

	class Meta:
		verbose_name = _('duration')
