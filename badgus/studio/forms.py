import re

from django import forms
from django.core.files.base import ContentFile

from .datauri import DataURI
from .models import Design
from .widgets import *

COMPLEX_INPUT_REGEX = r'(?P<key>\w+)\[(?P<value>[^\]]+)\]'
_COMPLEX_INPUT_RE = re.compile('^{0}$'.format(COMPLEX_INPUT_REGEX))


class ExtendedModelChoiceIterator (forms.models.ModelChoiceIterator):

    class Choice (object):
        def __init__ (self, value, label, context):
            self.value = value
            self.label = label
            self.context = context

        def __iter__ (self):
            yield self.value
            yield self.label

        def __getitem__ (self, index):
            if index == 0:
                return self.value
            if index == 1:
                return self.label
            if index == 2 and self.context:
                return self.context
            if type(index) is not int:
                raise TypeError
            raise IndexError

        def __len__ (self):
            return 3 if self.context else 2

    def choice(self, obj):
        return self.Choice(self.field.prepare_value(obj), self.field.label_from_instance(obj), obj)


class DesignForm (forms.ModelForm):
    is_design = forms.IntegerField(initial=1, widget=forms.HiddenInput)

    class Meta:
        model = Design

        localized_fields = '__all__'
        widgets = {
            'template': TemplateInput,
            'palette': PaletteInput,
            'colors': ColorsInput,
            'mask': MaskInput,
            'options': OptionsInput,
            'glyph': GlyphInput,
            'image': ImageInput,
        }

    def __init__(self, data=None, *args, **kwargs):
        if data is not None:
            query = data.copy()
            if 'image' in data:
                try:
                    # Attempt to parse as data URI first
                    # If that fails, it'll be dealt with upstream
                    image = DataURI(query['image'])
                    query['image'] = ContentFile(image.data, 'graphic.png')
                except ValueError:
                    pass

            complex_input = {}

            for key, value in query.items():
                match = _COMPLEX_INPUT_RE.match(key)
                if match:
                    del query[key]
                    input_key = match.group('key')
                    input_value = match.group('value')
                    if input_key not in complex_input:
                        complex_input[input_key] = {}
                    complex_input[input_key][input_value] = value

            for key, value in complex_input.items():
                if key not in query or type(query[key]) != dict:
                    query[key] = {}
                query[key].update(value)

            if 'palette' in query and query['palette']:
                query.pop('colors')

            data = query

        kwargs.setdefault('auto_id', 'studio-%s')
        kwargs.setdefault('label_suffix', '')
        super(DesignForm, self).__init__(data, *args, **kwargs)

        for name, field in self.fields.items():
            if hasattr(field, 'choices'):
                required = field.required or getattr(field.widget, 'required', False)
                field.empty_label = None if required else 'None'
                field.choices = ExtendedModelChoiceIterator(field)
                field.widget.choices = field.choices

