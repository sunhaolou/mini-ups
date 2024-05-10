

from django.urls import path

from . import views

urlpatterns = [
    path("",views.index, name="index"),
    path("service", views.service_view, name="service"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("signup", views.signup_view, name="signup"),
    path("profile", views.profile_view, name="profile"),
    path("profile/edit", views.profileUpdate_view, name="profileUpdate"),
    path("profile/password", views.passwordChange_view, name='passwordUpdate'),
    path("logout", views.logout_view, name="logout"),
    path('package-detail/<int:package_id>/', views.package_detail_view, name='package-detail'),
    path('public-search/<int:tracking_number>/', views.public_package_view, name='public-search'),
    path('test',views.test, name='test'),
    path('update-destination/<int:package_id>/', views.update_destination, name='update_destination'),
    path('forgetpassword', views.forget_password, name='forget_password'),
    path('password-reset-request', views.password_reset_request, name='password_reset_request'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('contact_email', views.contact_email, name='contact_email'),
    path('password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),
    path('contact', views.contact_view, name='contact'),

    path('subscribe', views.subscribe_email, name='subscribe_email'),


]