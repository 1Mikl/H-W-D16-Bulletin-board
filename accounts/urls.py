from django.urls import path, include
from .views import SignUp

urlpatterns = [
    path('signup', SignUp.as_view(), name='signup'),
]