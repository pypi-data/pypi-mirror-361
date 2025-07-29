from django.conf import settings

if getattr(settings, 'ENABLE_DYNAMIC_TEXT_TRANSLATIONS', False):
    from modeltranslation.translator import translator, TranslationOptions
    from .models import DynamicText

    class DynamicTextTranslationOptions(TranslationOptions):
        fields = ('title', 'content',)

    translator.register(DynamicText, DynamicTextTranslationOptions)