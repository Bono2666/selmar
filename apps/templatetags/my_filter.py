import os

from django import template


register = template.Library()


@register.filter
def filename(value):
    return os.path.basename(value.file.name)


@register.filter
def to_space(value):
    return value.replace('%20', ' ').replace('25', '')
