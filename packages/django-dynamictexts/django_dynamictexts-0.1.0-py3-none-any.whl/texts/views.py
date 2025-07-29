from django.views.generic import TemplateView

class DynamicTextTestView(TemplateView):
    template_name = 'test_dynamictext.html'
