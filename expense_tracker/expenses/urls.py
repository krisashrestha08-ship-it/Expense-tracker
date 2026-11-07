from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # CRUD
    path('', views.expense_list, name='expense_list'),
    path('add/', views.expense_create, name='expense_create'),
    path('edit/<int:pk>/', views.expense_update, name='expense_update'),
    path('delete/<int:pk>/', views.expense_delete, name='expense_delete'),
]
