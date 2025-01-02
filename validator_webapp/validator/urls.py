from django.urls import path
from . import views
from .views import deed_list, get_ship_names, get_roles, get_organizations, CustomLoginView, CustomLogoutView

urlpatterns = [
    path('verify_deed/', views.first_deed, name='first_deed'),
    path('verify_deed/<int:deed_id>/', views.verify_deed, name='verify_deed'),
    path('deeds/', deed_list, name='deed_list'),
    path('ship-names/', get_ship_names, name='get_ship_names'),
    path('roles/', get_roles, name='get_roles'),
    path('organizations/', get_organizations, name='get_organizations'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    ]