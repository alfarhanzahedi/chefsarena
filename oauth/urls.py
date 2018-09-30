from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import success

urlpatterns = [
    path('success', success),
    path('logout', LogoutView.as_view(), name = 'logout'),
]