# urls.py in your Django app
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_sailors_soldiers/', views.get_sailors_soldiers, name='get_sailors_soldiers'),
]
