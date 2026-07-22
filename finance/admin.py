from django.contrib import admin
from .models import Profile, Category, Income, Expense, MonthlyBudget

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency')
    search_fields = ('user__username', 'user__email')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'source', 'date')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'source', 'description')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'payment_method', 'date')
    list_filter = ('date', 'category', 'payment_method', 'user')
    search_fields = ('user__username', 'description')

@admin.register(MonthlyBudget)
class MonthlyBudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'year', 'budget')
    list_filter = ('month', 'year', 'user')
    search_fields = ('user__username',)
