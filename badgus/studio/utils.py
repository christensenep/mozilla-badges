import cgi
from django.utils.encoding import force_text


def escape (str):
    return cgi.escape(force_text(str), quote=True)


def flatten_attrs (attrs={}):
    return ''.join([' %s="%s"' % (key, escape(value))
                        for key, value in sorted(attrs.items())])

