from .models import (Design, Template, Palette, Color, Mask, Glyph)

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse


def _render_image (image, size=100):
    try:
        return '<img src="%s" width="%d">' % (image.url, size,)
    except ValueError:
        return 'No preview available'
    

def _object_admin_url (obj):
    return reverse('admin:%s_%s_change' %(obj._meta.app_label,  obj._meta.module_name),  args=[obj.id] )


def _display_object (obj, linked=True):
    if object is None:
        return '(None)'
    if not linked:
        return unicode(obj)
    return '<a href="%s">%s</a>' % (_object_admin_url(obj), unicode(obj))


def _make_display_method (name, prop=None):
    if prop is None:
        prop = name.lower()
    def method (self, obj=None):
        if obj is None:
            obj = self
        return _display_object(getattr(obj, prop, None))
    method.allow_tags = True
    method.short_description = name
    return method


class IsNullFieldListFilter(admin.FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '%s__isnull' % field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        super(IsNullFieldListFilter, self).__init__(field,
            request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def choices(self, cl):
        for lookup, title in (
                (None, _('All')),
                ('False', _('Yes')),
                ('True', _('No'))):
            yield {
                'selected': self.lookup_val == lookup,
                'query_string': cl.get_query_string({
                        self.lookup_kwarg: lookup,
                    }),
                'display': title,
            }


class DesignAdmin(admin.ModelAdmin):
    _template = _make_display_method('Template')
    _palette = _make_display_method('Color Palette', 'palette')
    _mask = _make_display_method('Mask')
    _glyph = _make_display_method('Glyph')
    _badge = _make_display_method('Badge')
    _creator = _make_display_method('Creator')

    def _design (self):
        return _render_image(self.image)
    _design.allow_tags = True
    _design.short_description = 'Design'

    def _image (self, obj):
        return _render_image(obj.image)
    _image.allow_tags = True
    _image.short_description = 'Image'

    def _colors (self, obj):
        if not obj.colors:
            return '(None)'

        return '<br>'.join(['%s: <code>%s</code>' % (key.capitalize(), value.upper())
                            for key, value in obj.colors.items()])
    _colors.allow_tags = True
    _colors.short_description = 'Colors'

    def _options (self, obj):
        if not obj.options:
            return '(None)'

        return '<br>'.join(['%s: <code>%s</code>' % (key.capitalize(), value.upper())
                            for key, value in obj.options.items()])
    _options.allow_tags = True
    _options.short_description = 'Options'

    list_display = (_design, _badge, _creator, _glyph, 'created',)
    list_filter = (('badge', IsNullFieldListFilter), 'template', 'palette')
    fieldsets = ((None, {'fields':('_image', 'created',)}),
                    ('Meta', {'fields':('_template', '_palette', '_colors',
                                        '_mask', '_options', '_glyph',)}),
                    ('related', {'fields':('_badge', '_creator',)}))
    readonly_fields = ('_template', '_palette', '_colors', '_mask', '_options', '_glyph',
                        '_badge', '_image', '_creator', 'created')

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'creator', None) is None:
            obj.creator = request.user
        if obj.creator.is_anonymous:
            raise ValidationError('Creator cannot be anonymous')
        obj.save()

class TemplateAdmin(admin.ModelAdmin):
    def img (self):
        return '<img src="%s" width="100">' % self.svg.url
    img.allow_tags = True
    img.short_description = 'Image'

    list_display = ('name', 'restricted', img,)
    list_editable = ('restricted',)


class PaletteAdmin(admin.ModelAdmin):
    class ColorInline(admin.TabularInline):
        model = Color

    def colors_list (self):
        out = []
        for color in self.colors.all():
            out.append('<span style="width: 1em; height: 1em; background: %s; display: inline-block; border: solid 1px black;"></span> %s'
                        % (color.value, color))
        return '<br>'.join(out)
    colors_list.allow_tags = True
    colors_list.short_description = 'Colors'

    list_display = ('name', colors_list, 'restricted')
    list_editable = ('restricted',)
    inlines = (ColorInline,)


class MaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'restricted',)
    list_editable = ('restricted',)


class GlyphAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('//maxcdn.bootstrapcdn.com/font-awesome/4.1.0/css/font-awesome.min.css',)}

    def with_icon (self):
        return '<span style="display: inline-block; width: 1.5em; font-size: 2em; vertical-align: middle;"><i class="fa fa-%s"></i></span> %s' % (self.reference, self)
    with_icon.allow_tags = True
    with_icon.short_description = 'Glyph'
    with_icon.admin_order_field = 'display'

    list_display = (with_icon, 'restricted',)
    list_filter = ('restricted',)
    list_editable = ('restricted',)


for x in ((Design, DesignAdmin),
          (Template, TemplateAdmin),
          (Palette, PaletteAdmin),
          (Mask, MaskAdmin),
          (Glyph, GlyphAdmin),):
    admin.site.register(*x)
