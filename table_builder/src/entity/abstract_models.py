from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from table_builder.src.services.constants import OrderChoice, NumberWhereChoice, StringWhereChoice


class ShowSection(models.Model):
	show = models.BooleanField(
		verbose_name=_('показать в результатах запроса'),
		default=True
	)

	class Meta:
		abstract = True


class AliasSection(models.Model):
	alias = models.CharField(
		verbose_name=_('псевдоним'),
		max_length=255,
		blank=True,
	)

	class Meta:
		abstract = True


class OrderSection(models.Model):
	order_predicate = models.CharField(
		verbose_name=_('условие сортировки'),
		choices=OrderChoice.choices,
		max_length=255,
		blank=True
	)
	order_priority = models.IntegerField(
		verbose_name=_('приоритет сортировки'),
		default=1,
	)

	class Meta:
		abstract = True


class WhereSection(models.Model):
	where_not = models.BooleanField(
		verbose_name=_('не'),
	)

	class Meta:
		abstract = True


class NumberWhereSection(WhereSection):
	where_predicate = models.CharField(
		verbose_name=_('условие фильтрации'),
		choices=NumberWhereChoice.choices,
		blank=True,
		max_length=255
	)

	class Meta:
		abstract = True


class IntegerNumberWhereSection(NumberWhereSection):
	where_value = models.IntegerField(
		verbose_name=_('значение фильтрации'),
		blank=True,
		null=True
	)

	class Meta:
		abstract = True


class FloatNumberWhereSection(NumberWhereSection):
	where_value = models.FloatField(
		verbose_name=_('значение фильтрации'),
		blank=True,
		null=True
	)

	class Meta:
		abstract = True


class StringWhereSection(WhereSection):
	where_predicate = models.CharField(
		verbose_name=_('условие фильтрации'),
		choices=StringWhereChoice.choices,
		blank=True,
		max_length=255
	)

	class Meta:
		abstract = True


class CharStringWhereSection(StringWhereSection):
	where_value = models.CharField(
		verbose_name=_('значение фильтрации'),
		blank=True,
		max_length=255
	)

	class Meta:
		abstract = True


class DateWhereSection(WhereSection):
	where_from_value = models.DateField(
		verbose_name=_('от'),
		blank=True,
		null=True
	)
	where_to_value = models.DateField(
		verbose_name=_('до'),
		blank=True,
		null=True
	)

	class Meta:
		abstract = True


class DateTimeWhereSection(WhereSection):
	where_from_value = models.DateTimeField(
		verbose_name=_('от'),
		blank=True,
		null=True
	)
	where_to_value = models.DateTimeField(
		verbose_name=_('до'),
		blank=True,
		null=True
	)

	class Meta:
		abstract = True


class DurationWhereSection(WhereSection):
	where_from_value = models.DurationField(
		verbose_name=_('от'),
		blank=True,
		null=True
	)
	where_to_value = models.DurationField(
		verbose_name=_('до'),
		blank=True,
		null=True
	)

	class Meta:
		abstract = True


class ColumnRelation(models.Model):
	content_type = models.ForeignKey(
		to=ContentType,
		on_delete=models.CASCADE,
	)
	object_id = models.PositiveIntegerField()
	column_set = GenericForeignKey()

	class Meta:
		abstract = True


class Column(models.Model):
	name = models.CharField(
		verbose_name=_('имя столбца'),
		max_length=255
	)
	position = models.IntegerField(
		verbose_name=_('позиция'),
	)
	visible = models.BooleanField(
		verbose_name=_('видим на форме'),
		default=True
	)

	class Meta:
		abstract = True

	def __str__(self):
		return f'Column(pk={self.pk}, name={self.name})'
