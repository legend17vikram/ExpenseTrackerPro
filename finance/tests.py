from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
import datetime

from .models import Category, Expense, MonthlyBudget
from .services import calculate_budget_forecast

class FinanceAppTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        # Fetch pre-seeded test categories from the data migration
        self.category_food = Category.objects.get(name='Food')
        self.category_bills = Category.objects.get(name='Bills')

    def test_profile_creation_signal(self):
        """Verify that a user profile is automatically initialized on user registration"""
        self.assertIsNotNone(self.user.profile)
        self.assertEqual(self.user.profile.currency, 'USD')

    def test_expense_creation_and_validation(self):
        """Test expense logs additions and Category relations"""
        expense = Expense.objects.create(
            user=self.user,
            amount=Decimal('45.50'),
            category=self.category_food,
            description='Lunch at diner',
            payment_method='Cash',
            date=datetime.date.today()
        )
        self.assertEqual(expense.amount, Decimal('45.50'))
        self.assertEqual(expense.category.name, 'Food')

    def test_budget_forecast_moving_average(self):
        """Test that the Simple Moving Average forecast algorithm works correctly"""
        today = datetime.date.today()
        
        # Log expenses in Month -1, -2, and -3
        # Month -1
        m1 = today.month - 1
        y1 = today.year
        if m1 <= 0: 
            m1 += 12
            y1 -= 1
        Expense.objects.create(user=self.user, amount=Decimal('300.00'), category=self.category_bills, date=datetime.date(y1, m1, 15))

        # Month -2
        m2 = today.month - 2
        y2 = today.year
        if m2 <= 0: 
            m2 += 12
            y2 -= 1
        Expense.objects.create(user=self.user, amount=Decimal('200.00'), category=self.category_bills, date=datetime.date(y2, m2, 10))

        # Month -3
        m3 = today.month - 3
        y3 = today.year
        if m3 <= 0: 
            m3 += 12
            y3 -= 1
        Expense.objects.create(user=self.user, amount=Decimal('400.00'), category=self.category_bills, date=datetime.date(y3, m3, 5))

        # Configure budget limit for the current month
        MonthlyBudget.objects.create(user=self.user, month=today.month, year=today.year, budget=Decimal('250.00'))

        # Forecast calculation check (SMA of 300, 200, 400 = 300.00)
        forecast_amount, forecast_warning, current_budget = calculate_budget_forecast(self.user)

        self.assertEqual(forecast_amount, 300.00)
        self.assertEqual(current_budget, 250.00)
        self.assertTrue(forecast_warning)  # 300 exceeds 250 budget limit, so warning must be True
