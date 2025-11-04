from django.views.generic import TemplateView

class HomeView(TemplateView):
    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ["home/home_logged_in.html"]
        else:
            return ["home/home_logged_out.html"]