from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('auth_referral.urls')),
    path('profile/', include('profile_referral.urls')),
]
