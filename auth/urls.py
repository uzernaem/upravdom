from django.urls import path
from auth.views import MyObtainTokenPairView, RegisterView
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
 
admin.site.index_title = _('Управление многоквартирным домом')
admin.site.site_header = _('Панель администратора')
admin.site.site_title = _('Управление многоквартирным домом')


urlpatterns = [
    path('login', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('register', RegisterView.as_view(), name='auth_register'),
]