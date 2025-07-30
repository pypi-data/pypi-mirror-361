from django.db import models

from content_framework import fields as cf_fields
from . import widgets
from .utils import is_jsonable


class ModelSerializer:
    def __init__(self, model: type[models.Model]):
        self.model = model

    widgets = {
        models.CharField: widgets.InputWidget,
        models.IntegerField: widgets.InputWidget,
        models.SmallIntegerField: widgets.InputWidget,
        models.BigIntegerField: widgets.InputWidget,
        models.PositiveIntegerField: widgets.InputWidget,
        models.PositiveSmallIntegerField: widgets.InputWidget,
        models.PositiveBigIntegerField: widgets.InputWidget,
        models.FloatField: widgets.InputWidget,
        models.DecimalField: widgets.InputWidget,
        models.SlugField: widgets.SlugWidget,
        models.TextField: widgets.TextAreaWidget,
        models.BooleanField: widgets.BooleanWidget,
        models.NullBooleanField: widgets.BooleanWidget,
        cf_fields.MultipleChoiceField: widgets.MultipleChoiceWidget,
        cf_fields.TagField: widgets.TagWidget,
        cf_fields.HTMLField: widgets.RichTextWidget,
        cf_fields.URLPathField: widgets.URLPathWidget,
    }

    def serialize(self):
        model = self.model

        return {
            "label": model._meta.label,
            "verbose_name": model._meta.verbose_name,
            "verbose_name_plural": model._meta.verbose_name_plural,
            "fields": self.get_fields(),
        }

    def get_fields(self):
        fields = {}

        for field in self.model._meta.fields:
            fields[field.name] = self.get_field(field)

        return fields

    def get_field(self, field):
        widget = self.get_widget(field)

        data = {
            "verbose_name": field.verbose_name,
            "required": not field.null or not field.blank,
        }

        if field.help_text:
            data["help_text"] = field.help_text

        if is_jsonable(field.default):
            data["default"] = field.default

        if widget:
            data["widget"] = widget

        if not field.editable:
            data["readonly"] = True

        if field.primary_key:
            data["primary_key"] = True
            data["readonly"] = True

        if getattr(field, "choices", None) is not None:
            data["choices"] = field.choices

        if getattr(field, "max_length", None) is not None:
            data["max_length"] = field.max_length

        return data

    def get_widget(self, field):
        try:
            return self.widgets[field.__class__].__name__
        except KeyError:
            return None
