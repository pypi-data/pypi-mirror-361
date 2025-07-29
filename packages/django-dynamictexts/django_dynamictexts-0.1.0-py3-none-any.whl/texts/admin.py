from . import translation
from django.contrib import admin
from .models import DynamicText
from modeltranslation.admin import TabbedTranslationAdmin

@admin.register(DynamicText)
class DynamicTextAdmin(TabbedTranslationAdmin):
    list_display = ('key', 'title')
    search_fields = ('key', 'title')
