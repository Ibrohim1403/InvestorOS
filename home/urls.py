from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import CustomAuthenticationForm
from . import views

urlpatterns = [
    path("morning_brief/", views.morning_brief, name="morning_brief"),
    path("analytics/", views.analytics, name="analytics"),
    path("settings/", views.settings_page, name="settings"),
    path("send-email/<int:user_id>/", views.send_email, name="send_email"),
    path("register/", views.register, name="register"),
    path('reports/', views.reports, name='reports'),
    path("", auth_views.LoginView.as_view(
        template_name="login.html",
        authentication_form=CustomAuthenticationForm
    ), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
]
