from django.contrib import admin
from table_builder import models
from django.contrib.contenttypes.admin import GenericTabularInline


class SingleValueColumnMeta:
	fields = (
		'name', 'visible', 'position', 'show', 'alias', 'where_not', 'where_predicate', 'where_value',
		'order_predicate', 'order_priority'
	)
	extra = 0


class MultiValueColumnMeta:
	fields = (
		'name', 'visible', 'position', 'show', 'alias', 'where_not', 'where_from_value', 'where_to_value',
		'order_predicate', 'order_priority'
	)
	extra = 0


class IntegerColumnInline(SingleValueColumnMeta, GenericTabularInline):
	model = models.IntegerColumn


class FloatColumnInline(SingleValueColumnMeta, GenericTabularInline):
	model = models.FloatColumn


class CharColumnInline(SingleValueColumnMeta, GenericTabularInline):
	model = models.CharColumn


class DateColumnInline(MultiValueColumnMeta, GenericTabularInline):
	model = models.DateColumn


class DateTimeColumnInline(MultiValueColumnMeta, GenericTabularInline):
	model = models.DateTimeColumn


class DurationColumnInline(MultiValueColumnMeta, GenericTabularInline):
	model = models.DurationColumn


@admin.register(models.Database)
class DatabaseAdminModel(admin.ModelAdmin):
	list_display = ('dbname', 'dialect', 'alias')
	fieldsets = (
		('Основные настройки', {'fields': ('dbname', 'dialect', 'user', 'password', 'host', 'port')}),
		('Дополнительные настройки', {'fields': ('alias', 'auto_fill_template'), 'classes': ('wide',)})
	)


@admin.register(models.Table)
class TableAdminModel(admin.ModelAdmin):
	list_display = ('name', 'alias', 'database')
	inlines = (
		IntegerColumnInline, FloatColumnInline, CharColumnInline, DateColumnInline,
		DateTimeColumnInline, DurationColumnInline
	)


@admin.register(models.AutoFillTemplate)
class AutoFillTemplateAdminModel(admin.ModelAdmin):
	list_display = ('name', 'description')
	inlines = (
		IntegerColumnInline, FloatColumnInline, CharColumnInline, DateColumnInline,
		DateTimeColumnInline, DurationColumnInline
	)
