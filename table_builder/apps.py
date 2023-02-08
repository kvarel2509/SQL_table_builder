from django.apps import AppConfig


class TableBuilderConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'table_builder'
	verbose_name = "SQL запросы"
