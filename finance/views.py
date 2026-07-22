from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.utils.dateparse import parse_date
from django.http import HttpResponse
import datetime
import csv

from .models import Income, Expense, Category, MonthlyBudget
from .forms import UserRegistrationForm, IncomeForm, ExpenseForm, MonthlyBudgetForm
from .services import calculate_budget_forecast

# ==========================================
# AUTHENTICATION & PORTAL VIEWS
# ==========================================

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            messages.success(request, "Your registration was successful! You can now log in.")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user
    today = datetime.date.today()
    current_month = today.month
    current_year = today.year

    # Aggregate financial balances
    total_income = Income.objects.filter(user=user).aggregate(sum=Sum('amount'))['sum'] or 0.0
    total_expense = Expense.objects.filter(user=user).aggregate(sum=Sum('amount'))['sum'] or 0.0
    current_balance = float(total_income) - float(total_expense)

    # Monthly statistics
    monthly_income = Income.objects.filter(user=user, date__month=current_month, date__year=current_year).aggregate(sum=Sum('amount'))['sum'] or 0.0
    monthly_expense = Expense.objects.filter(user=user, date__month=current_month, date__year=current_year).aggregate(sum=Sum('amount'))['sum'] or 0.0

    # Budget retrieval
    budget_record = MonthlyBudget.objects.filter(user=user, month=current_month, year=current_year).first()
    monthly_budget = float(budget_record.budget) if budget_record else 0.0
    remaining_budget = monthly_budget - float(monthly_expense)
    savings = float(monthly_income) - float(monthly_expense)

    # Warnings for exceeding budgets
    budget_warning = False
    if monthly_budget > 0 and float(monthly_expense) > monthly_budget:
        budget_warning = True

    # Moving Average budget forecasting calculation
    forecast_amount, forecast_warning, _ = calculate_budget_forecast(user)

    # Retrieve recent transactions
    recent_incomes = list(Income.objects.filter(user=user).order_by('-date')[:5])
    recent_expenses = list(Expense.objects.filter(user=user).order_by('-date')[:5])
    
    # Combine and sort transactions by date desc
    transactions = []
    for inc in recent_incomes:
        transactions.append({'type': 'income', 'object': inc, 'date': inc.date})
    for exp in recent_expenses:
        transactions.append({'type': 'expense', 'object': exp, 'date': exp.date})
    
    transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)[:5]

    # --- ANALYTICS CALCULATIONS ---

    # 1. Expense Category Pie Chart (Current Month)
    category_expenses = Expense.objects.filter(
        user=user, date__month=current_month, date__year=current_year
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')
    
    category_labels = [item['category__name'] or 'Uncategorized' for item in category_expenses]
    category_data = [float(item['total']) for item in category_expenses]

    # 2. Highest Spending Category
    highest_category = category_labels[0] if category_labels else 'None'
    highest_category_amount = category_data[0] if category_data else 0.0

    # 3. Average Daily Spending (Current Month)
    days_in_month = today.day
    avg_daily_spending = float(monthly_expense) / days_in_month if days_in_month > 0 else 0.0

    # 4. Daily Spending Trend (Line Chart - Current Month)
    daily_expenses = Expense.objects.filter(
        user=user, date__month=current_month, date__year=current_year
    ).values('date__day').annotate(total=Sum('amount')).order_by('date__day')
    
    daily_trend_labels = [str(d) for d in range(1, today.day + 1)]
    daily_trend_data = [0.0] * today.day
    
    for item in daily_expenses:
        day_idx = item['date__day'] - 1
        if day_idx < len(daily_trend_data):
            daily_trend_data[day_idx] = float(item['total'])

    # 5. Last Six Months Overview (Bar Chart)
    six_months_labels = []
    six_months_income = []
    six_months_expense = []
    
    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        if m <= 0:
            m += 12
            y -= 1
            
        month_date = datetime.date(y, m, 1)
        month_name = month_date.strftime('%b')  # Short month name
        six_months_labels.append(month_name)
        
        inc_sum = Income.objects.filter(user=user, date__month=m, date__year=y).aggregate(sum=Sum('amount'))['sum'] or 0.0
        exp_sum = Expense.objects.filter(user=user, date__month=m, date__year=y).aggregate(sum=Sum('amount'))['sum'] or 0.0
        
        six_months_income.append(float(inc_sum))
        six_months_expense.append(float(exp_sum))

    context = {
        'title': 'Dashboard',
        'username': user.username,
        'name': f"{user.first_name} {user.last_name}",
        'email': user.email,
        'current_balance': current_balance,
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
        'monthly_budget': monthly_budget,
        'remaining_budget': remaining_budget,
        'savings': savings,
        'budget_warning': budget_warning,
        'recent_transactions': transactions,
        
        # Forecast data
        'forecast_amount': forecast_amount,
        'forecast_warning': forecast_warning,
        
        # Analytics context data
        'category_labels': category_labels,
        'category_data': category_data,
        'highest_category': highest_category,
        'highest_category_amount': highest_category_amount,
        'avg_daily_spending': avg_daily_spending,
        
        'daily_trend_labels': daily_trend_labels,
        'daily_trend_data': daily_trend_data,
        
        'six_months_labels': six_months_labels,
        'six_months_income': six_months_income,
        'six_months_expense': six_months_expense
    }
    return render(request, 'finance/dashboard.html', context)


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        currency = request.POST.get('currency', 'USD')

        if not first_name or not last_name or not email:
            messages.error(request, "Please fill out all required fields.")
        elif User.objects.exclude(pk=user.pk).filter(email=email).exists():
            messages.error(request, "An account with this email address already exists.")
        else:
            with transaction.atomic():
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()
                
                profile = user.profile
                profile.currency = currency
                profile.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
    return render(request, 'finance/profile.html')


# ==========================================
# INCOME MANAGEMENT (CRUD)
# ==========================================

@login_required
def income_list(request):
    user = request.user
    incomes = Income.objects.filter(user=user).order_by('-date')
    return render(request, 'finance/income_list.html', {'incomes': incomes})


@login_required
def income_create(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                income = form.save(commit=False)
                income.user = request.user
                income.save()
            messages.success(request, "Income entry logged successfully!")
            return redirect('income_list')
    else:
        form = IncomeForm(initial={'date': datetime.date.today()})
    return render(request, 'finance/income_form.html', {'form': form, 'action': 'Add'})


@login_required
def income_update(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            messages.success(request, "Income entry updated successfully!")
            return redirect('income_list')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'finance/income_form.html', {'form': form, 'action': 'Edit'})


@login_required
def income_delete(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        with transaction.atomic():
            income.delete()
        messages.success(request, "Income entry deleted successfully!")
        return redirect('income_list')
    return render(request, 'finance/income_confirm_delete.html', {'income': income})


# ==========================================
# EXPENSE MANAGEMENT (CRUD with FILTERS)
# ==========================================

@login_required
def expense_list(request):
    user = request.user
    expenses = Expense.objects.filter(user=user).order_by('-date')
    categories = Category.objects.all().order_by('name')

    # Apply search query filter
    search_query = request.GET.get('search', '')
    if search_query:
        expenses = expenses.filter(
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(payment_method__icontains=search_query)
        )

    # Apply category filter
    category_id = request.GET.get('category', '')
    if category_id:
        expenses = expenses.filter(category_id=category_id)

    # Apply date range filtering
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    
    if start_date_str:
        start_date = parse_date(start_date_str)
        if start_date:
            expenses = expenses.filter(date__gte=start_date)
            
    if end_date_str:
        end_date = parse_date(end_date_str)
        if end_date:
            expenses = expenses.filter(date__lte=end_date)

    context = {
        'expenses': expenses,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'start_date': start_date_str,
        'end_date': end_date_str
    }
    return render(request, 'finance/expense_list.html', context)


@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                expense = form.save(commit=False)
                expense.user = request.user
                expense.save()

                # Trigger Budget exceed warnings
                exp_date = expense.date
                total_monthly_expenses = Expense.objects.filter(
                    user=request.user, 
                    date__month=exp_date.month, 
                    date__year=exp_date.year
                ).aggregate(sum=Sum('amount'))['sum'] or 0.0
                
                budget_record = MonthlyBudget.objects.filter(
                    user=request.user, 
                    month=exp_date.month, 
                    year=exp_date.year
                ).first()
                
                if budget_record and float(total_monthly_expenses) > float(budget_record.budget):
                    messages.warning(
                        request, 
                        f"WARNING: Your total expenses for {exp_date.strftime('%B %Y')} "
                        f"({total_monthly_expenses} {request.user.profile.currency}) "
                        f"have exceeded your set budget limits ({budget_record.budget} {request.user.profile.currency})!"
                    )
                else:
                    messages.success(request, "Expense entry logged successfully!")
            
            return redirect('expense_list')
    else:
        form = ExpenseForm(initial={'date': datetime.date.today()})
    return render(request, 'finance/expense_form.html', {'form': form, 'action': 'Add'})


@login_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                
                # Check budget limits again
                exp_date = expense.date
                total_monthly_expenses = Expense.objects.filter(
                    user=request.user, 
                    date__month=exp_date.month, 
                    date__year=exp_date.year
                ).aggregate(sum=Sum('amount'))['sum'] or 0.0
                
                budget_record = MonthlyBudget.objects.filter(
                    user=request.user, 
                    month=exp_date.month, 
                    year=exp_date.year
                ).first()
                
                if budget_record and float(total_monthly_expenses) > float(budget_record.budget):
                    messages.warning(
                        request, 
                        f"WARNING: Your updated expenses for {exp_date.strftime('%B %Y')} "
                        f"({total_monthly_expenses} {request.user.profile.currency}) "
                        f"have exceeded your set budget limits ({budget_record.budget} {request.user.profile.currency})!"
                    )
                else:
                    messages.success(request, "Expense entry updated successfully!")
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'finance/expense_form.html', {'form': form, 'action': 'Edit'})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        with transaction.atomic():
            expense.delete()
        messages.success(request, "Expense entry deleted successfully!")
        return redirect('expense_list')
    return render(request, 'finance/expense_confirm_delete.html', {'expense': expense})


# ==========================================
# BUDGET SETTINGS
# ==========================================

@login_required
def budget_settings(request):
    user = request.user
    today = datetime.date.today()
    
    # Try fetching existing budget for current month/year
    budget_instance = MonthlyBudget.objects.filter(user=user, month=today.month, year=today.year).first()
    
    if request.method == 'POST':
        form = MonthlyBudgetForm(request.POST, instance=budget_instance)
        if form.is_valid():
            with transaction.atomic():
                budget = form.save(commit=False)
                budget.user = user
                budget.save()
            messages.success(request, "Monthly budget configured successfully!")
            return redirect('dashboard')
    else:
        if budget_instance:
            form = MonthlyBudgetForm(instance=budget_instance)
        else:
            form = MonthlyBudgetForm(initial={'month': today.month, 'year': today.year, 'budget': 0.0})
            
    # Fetch list of historical budgets
    budgets = MonthlyBudget.objects.filter(user=user).order_by('-year', '-month')
    
    context = {
        'form': form,
        'budgets': budgets
    }
    return render(request, 'finance/budget_settings.html', context)


# ==========================================
# ADVANCED CSV EXPORT FEATURE
# ==========================================

@login_required
def export_expenses_csv(request):
    user = request.user
    expenses = Expense.objects.filter(user=user).order_by('-date')

    # Create HTTP Response with text/csv header content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="expenses_{user.username}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Description', 'Payment Method', f'Amount ({user.profile.currency})'])

    for exp in expenses:
        category_name = exp.category.name if exp.category else 'Uncategorized'
        writer.writerow([exp.date, category_name, exp.description, exp.payment_method, exp.amount])

    return response
