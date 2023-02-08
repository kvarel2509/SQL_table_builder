from django.db.models import CharField
from django import forms
from django.utils.translation import gettext_lazy as _


class PasswordField(CharField):
	#TODO шифрование паролей
	description = _('Custom string for specifying passwords')

	def formfield(self, **kwargs):
		defaults = {
			'widget': forms.PasswordInput,
		}
		defaults.update(kwargs)
		return super().formfield(**defaults)
