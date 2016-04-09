from django.views.generic import TemplateView


class SwaggerUI(TemplateView):
    template_name = 'rest_framework_swagger/index.html'
