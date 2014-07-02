from django import forms
from django.utils.encoding import force_text
from itertools import chain

from .utils import flatten_attrs


__all__ = [
    'TemplateInput',
    'PaletteInput',
    'ColorsInput',
    'MaskInput',
    'OptionsInput',
    'GlyphInput',
    'ImageInput',
]


class ComplexSelect (forms.Select):

    def get_option_attrs (self, obj=None):
        def lookup (context, attr):
            if not attr:
                return context

            parts = attr.split('.', 1) + [None]

            try:
                return lookup(getattr(context, parts.pop(0)), parts.pop(0))
            except AttributeError:
                return None

        if obj is None or not hasattr(self, 'object_attr_map'):
            return {}

        return dict([(key, lookup(obj, value)) for key, value in self.object_attr_map.iteritems()])

    def render_option (self, selected_choices, option_value, option_label, obj=None):
        attrs = dict(self.get_option_attrs(obj))

        if option_value is None:
            option_value = ''
        option_value = unicode(option_value)

        attrs['value'] = option_value

        if option_value in selected_choices:
            attrs['selected'] = 'selected'
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)

        return '<option%s>%s</option>' % (flatten_attrs(attrs), force_text(option_label))

    def render_options (self, choices, selected_choices):
        # Normalize to strings.
        selected_choices = set(force_text(v) for v in selected_choices)
        output = []
        for choice in chain(self.choices, choices):
            option_value = choice[0]
            option_label = choice[1]
            obj = None if len(choice) == 2 else choice[2]

            if isinstance(option_label, (list, tuple)):
                output.append(format_html('<optgroup label="{0}">', force_text(option_value)))
                for option in option_label:
                    output.append(self.render_option(selected_choices, *option))
                output.append('</optgroup>')
            else:
                output.append(self.render_option(selected_choices, option_value, option_label, obj))
        return '\n'.join(output)


class TemplateInput (ComplexSelect):
    object_attr_map = {
        'data-path': 'svg.url'
    }

    @classmethod
    def limit_choices (cls, queryset, user):
        queryset = queryset.filter(restricted=False)
        return queryset


class PaletteInput (ComplexSelect):
    required = True

    @classmethod
    def limit_choices (cls, queryset, user):
        queryset = queryset.filter(restricted=False)
        return queryset

    def get_option_attrs (self, obj=None):
        attrs = {}
        if hasattr(obj, 'colors'):
            for color in obj.colors.all():
                attrs['data-color-%s' % color.key] = color.value
        return attrs


class ColorsInput (forms.Widget):
    is_hidden = True

    def render (name, value, data, *args, **kwargs):
        attrs = {
            'id': 'custom-palette',
        }

        if data is not None:
            try:
                for key, value in data.items():
                    attrs['data-color-' + key] = value
            except AttributeError:
                # data probably not a dict - ignore it
                pass

        return '<div%s></div>' % flatten_attrs(attrs);


class MaskInput (ComplexSelect):
    object_attr_map = {
        'data-path': 'svg.url'
    }

    @classmethod
    def limit_choices (cls, queryset, user):
        queryset = queryset.filter(restricted=False)
        # print type(queryset), type(user)
        return queryset


class OptionsInput (forms.Widget):

    def render (name, value, data={}, *args, **kwargs):
        attrs = {
            'id': 'options',
        }

        if data is not None:
            try:
                for key, value in data.items():
                    attrs['data-' + key] = value
            except AttributeError:
                # data probably not a dict - ignore it
                pass

        return '<div%s><i>None</i></div>' % flatten_attrs(attrs);


class GlyphInput (ComplexSelect):
    object_attr_map = {
        'data-glyph': 'reference'
    }

    @classmethod
    def limit_choices (cls, queryset, user):
        queryset = queryset.filter(restricted=False)
        # print type(queryset), type(user)
        return queryset


class ImageInput (forms.HiddenInput):
    pass
