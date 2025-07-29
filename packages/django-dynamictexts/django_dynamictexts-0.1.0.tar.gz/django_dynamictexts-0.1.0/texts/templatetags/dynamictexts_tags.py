from django import template
from texts.models import DynamicText

register = template.Library()

@register.simple_tag
def get_title(key):
    try:
        return DynamicText.objects.get(key=key).title
    except DynamicText.DoesNotExist:
        return ''

@register.simple_tag
def get_content(key):
    try:
        return DynamicText.objects.get(key=key).content
    except DynamicText.DoesNotExist:
        return ''