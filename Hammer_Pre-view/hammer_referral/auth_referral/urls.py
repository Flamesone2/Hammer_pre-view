from django.urls import path
from .views import VerifyCodeView, RegisterOrLoginAPIView

urlpatterns = [
    path('register-login/', RegisterOrLoginAPIView.as_view(), name='register_or_login'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),

]
