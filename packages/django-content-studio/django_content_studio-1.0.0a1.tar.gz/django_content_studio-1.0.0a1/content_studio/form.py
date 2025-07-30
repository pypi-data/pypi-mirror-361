class Field:
    """
    Field class for configuring the fields in content edit views in Django Content Studio.
    """

    def __init__(self, name: str, col_span: int = 1):
        self.name = name
        self.col_span = col_span

    def serialize(self):
        return {
            "name": self.name,
            "col_span": self.col_span,
        }


class FieldLayout:
    """
    Field layout class for configuring the layout of fields in content edit views in Django Content Studio.
    """

    def __init__(self, fields: list[str | Field] = None, columns: int = 1):
        self.fields = fields or []
        self.columns = columns

    def serialize(self):
        return {
            "fields": [
                field.serialize() if isinstance(field, Field) else field
                for field in self.fields
            ],
            "columns": self.columns,
        }


class FormSet:
    """
    Formset class for configuring the blocks of fields in content edit views
    in Django Content Studio.
    """

    def __init__(
        self,
        title: str = "",
        description: str = "",
        fields: list[str | Field | FieldLayout] = None,
    ):
        self.title = title
        self.description = description
        self.fields = fields or []

    def serialize(self):
        return {
            "title": self.title,
            "description": self.description,
            "fields": [
                field.serialize() if isinstance(field, (Field, FieldLayout)) else field
                for field in self.fields
            ],
        }


class FormSetGroup:
    """
    Formset group class for configuring the groups of form sets in content edit views.
    """

    def __init__(self, label: str = "", formsets: list[FormSet] = None):
        self.label = label
        self.formsets = formsets or []

    def serialize(self):
        return {
            "label": self.label,
            "formsets": [formset.serialize() for formset in self.formsets],
        }
