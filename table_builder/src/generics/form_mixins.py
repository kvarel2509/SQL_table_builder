class AsDivFormMixin:
	"""
	An alternative way to display a form in a template via <div> tags
	"""
	def as_div(self):
		return self._html_output(
			normal_row='<div%(html_class_attr)s><div>%(label)s</div><div>%(errors)s%(field)s%(help_text)s</div></div>',
			error_row='<div><div colspan="2">%s</div></div>',
			row_ender='</div></div>',
			help_text_html='<br><span class="helptext">%s</span>',
			errors_on_separate_row=False,
		)
