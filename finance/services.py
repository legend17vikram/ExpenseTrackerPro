import datetime
from django.db.models import Sum
from .models import Expense, MonthlyBudget

def calculate_budget_forecast(user):
    """
    Calculates a Simple Moving Average (SMA) forecast for the current month's spending
    using expenses from the previous three months.
    
    Returns:
        forecast_amount (float): The projected spending for the current month.
        exceeds_budget (bool): True if projected spending exceeds the set budget.
        current_budget (float): The current month's budget limit.
    """
    today = datetime.date.today()
    total_spend_3_months = 0.0
    
    # Iterate through the past 3 months
    for i in range(1, 4):
        m = today.month - i
        y = today.year
        if m <= 0:
            m += 12
            y -= 1
            
        month_spend = Expense.objects.filter(
            user=user, 
            date__month=m, 
            date__year=y
        ).aggregate(sum=Sum('amount'))['sum'] or 0.0
        
        total_spend_3_months += float(month_spend)
        
    # Simple Moving Average calculation
    forecast_amount = total_spend_3_months / 3.0
    
    # Fetch current month's budget
    budget_record = MonthlyBudget.objects.filter(user=user, month=today.month, year=today.year).first()
    current_budget = float(budget_record.budget) if budget_record else 0.0
    
    # Flag budget warning
    exceeds_budget = False
    if current_budget > 0 and forecast_amount > current_budget:
        exceeds_budget = True
        
    return round(forecast_amount, 2), exceeds_budget, current_budget
