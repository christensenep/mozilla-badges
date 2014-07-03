from django.contrib.auth.models import User
from django.db import models

from badger.models import Badge, BADGE_UPLOADS_FS, mk_upload_to, slugify

from .fields import PickledObjectField
from .fontawesome import glyphs

try:
    import taggit
    from taggit.managers import TaggableManager
    from taggit.models import Tag, TaggedItem
except ImportError:
    taggit = None


class Template (models.Model):
    name = models.CharField(max_length=100, blank=False, unique=True,
            help_text='Template name.')
    svg = models.FileField(blank=False,
            storage=BADGE_UPLOADS_FS, upload_to=mk_upload_to('svg', 'svg'),
            verbose_name='SVG', help_text='SVG template file.')
    restricted = models.BooleanField(blank=False, default=False)

    created = models.DateTimeField(auto_now_add=True, blank=False)
    modified = models.DateTimeField(auto_now=True, blank=False)

    def __unicode__ (self):
        return self.name

    def get_upload_meta (self):
        return ("template", slugify(self.name))


class Palette (models.Model):
    name = models.CharField(max_length=100, blank=False, unique=True)
    restricted = models.BooleanField(blank=False, default=False)

    created = models.DateTimeField(auto_now_add=True, blank=False)
    modified = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        verbose_name='Color Palette'

    def __unicode__ (self):
        return self.name


class Color (models.Model):
    KEY_CHOICES = (
        ('background', 'Background'),
        ('stitching', 'Stitching'),
        ('border', 'Border'),
        ('detail', 'Detail'),
        ('glyph', 'Glyph'),
    )

    palette = models.ForeignKey(Palette, related_name='colors')
    key = models.CharField(max_length=20, blank=False,
            choices=KEY_CHOICES)
    value = models.CharField(max_length=7, blank=False)

    class Meta:
        unique_together = ('palette', 'key')

    def __unicode__ (self):
        return '%s: %s' % (self.get_key_display(), self.value)


class Mask (models.Model):
    name = models.CharField(max_length=100, blank=False, unique=True,
        help_text='Mask name')
    svg = models.FileField(blank=False,
            storage=BADGE_UPLOADS_FS, upload_to=mk_upload_to('svg', 'svg'),
            help_text='SVG template file')
    restricted = models.BooleanField(blank=False, default=False)

    created = models.DateTimeField(auto_now_add=True, blank=False)
    modified = models.DateTimeField(auto_now=True, blank=False)

    def __unicode__ (self):
        return self.name

    def get_upload_meta (self):
        return ("mask", slugify(self.name))


class Glyph (models.Model):
    reference = models.CharField(max_length=100, blank=False, unique=True,
        help_text='FontAwesome reference', choices=glyphs)
    name = models.CharField(max_length=100, blank=True, null=True, unique=True,
        help_text='Alternative name')
    restricted = models.BooleanField(blank=False, default=False)

    if taggit:
        tags = TaggableManager(blank=True)

    created = models.DateTimeField(auto_now_add=True, blank=False)
    modified = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        ordering = ['name', 'reference']

    def __unicode__ (self):
        if self.name:
            return self.name
        return self.get_reference_display();

    def display (self):
        return unicode(self)


class Design (models.Model):
    template = models.ForeignKey(Template, help_text="Template help")
    palette = models.ForeignKey(Palette, blank=True, null=True,
                                verbose_name='Color Palette',
                                help_text="Color Palette help")
    colors = PickledObjectField(blank=True, null=True)
    mask = models.ForeignKey(Mask, blank=True, null=True,
                                verbose_name='Background Mask',
                                help_text="Mask help")
    options = PickledObjectField(blank=True, null=True,
                                help_text="Options help")
    glyph = models.ForeignKey(Glyph, blank=True, null=True,
                                help_text="Glyph help")
    badge = models.ForeignKey(Badge, blank=True, null=True, unique=True, editable=False)
    image = models.ImageField(blank=False,
            storage=BADGE_UPLOADS_FS, upload_to=mk_upload_to('image', 'png'),
            help_text='Upload an image to represent the badge')

    creator = models.ForeignKey(User, blank=False, editable=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    modified = models.DateTimeField(auto_now=True, blank=False)

    def get_upload_meta (self):
        return ("design", "design")

    @classmethod
    def get_previous_for_user (cls, user):
        try:
            return cls.objects.get(creator=user, badge=None)
        except cls.DoesNotExist:
            return None

