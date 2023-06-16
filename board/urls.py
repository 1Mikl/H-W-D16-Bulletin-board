from django.urls import path, include
from .views import *


urlpatterns = [
   path('', PostsList.as_view(), name='home'),
   path('post/<int:pk>/', PostDetail.as_view(), name='post'),
   path('abouth/', PostAb.as_view(), name='abouth'),
   path('addpost/', PostCreate.as_view(), name='addpost'),
   path('post/<int:pk>/update/', PostUpdate.as_view(), name='post_update'),
   path('post/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
   path('response/<int:pk>', Respond.as_view(), name='response'),
   path('responses', Responses.as_view(), name='responses'),
   path('responses/<int:pk>', Responses.as_view(), name='responses'),
   path('response/accept/<int:pk>', response_accept),
   path('response/delete/<int:pk>', response_delete),
]