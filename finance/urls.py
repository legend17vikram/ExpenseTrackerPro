from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Income Management URLs
    path('income/', views.income_list, name='income_list'),
    path('income/create/', views.income_create, name='income_create'),
    path('income/<int:pk>/update/', views.income_update, name='income_update'),
    path('income/<int:pk>/delete/', views.income_delete, name='income_delete'),
    
    # Expense Management URLs
    path('expense/', views.expense_list, name='expense_list'),
    path('expense/create/', views.expense_create, name='expense_create'),
    path('expense/<int:pk>/update/', views.expense_update, name='expense_update'),
    path('expense/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    path('expense/export/csv/', views.export_expenses_csv, name='export_expenses_csv'),
    
    # Budget Management URLs
    path('budget/', views.budget_settings, name='budget_settings'),
]
