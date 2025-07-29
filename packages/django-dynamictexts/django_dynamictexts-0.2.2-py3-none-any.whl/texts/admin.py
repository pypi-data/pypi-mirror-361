from django.conf import settings
from django.contrib import admin
from .models import DynamicText

if getattr(settings, 'ENABLE_DYNAMIC_TEXT_TRANSLATIONS', False):
    from . import translation
    from modeltranslation.admin import TabbedTranslationAdmin

    @admin.register(DynamicText)
    class DynamicTextAdmin(TabbedTranslationAdmin):
        list_display = ('key', 'title')
        search_fields = ('key', 'title')
else:
    @admin.register(DynamicText)
    class DynamicTextAdmin(admin.ModelAdmin):
        list_display = ('key', 'title')
        search_fields = ('key', 'title')
