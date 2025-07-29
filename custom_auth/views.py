from allauth.account.views import PasswordChangeView
from django.urls import reverse


class CustomPasswordChangeView(PasswordChangeView):

    def get_success_url(self):
        return reverse('projects:projects_list')