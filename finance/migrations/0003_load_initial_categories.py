from django.db import migrations

def load_initial_categories(apps, schema_editor):
    Category = apps.get_model('finance', 'Category')
    default_categories = [
        {'name': 'Food', 'icon': 'fa-utensils'},
        {'name': 'Bills', 'icon': 'fa-file-invoice-dollar'},
        {'name': 'Shopping', 'icon': 'fa-cart-shopping'},
        {'name': 'Travel', 'icon': 'fa-plane'},
        {'name': 'Health', 'icon': 'fa-heart-pulse'},
        {'name': 'Education', 'icon': 'fa-user-graduate'},
        {'name': 'Entertainment', 'icon': 'fa-gamepad'},
        {'name': 'Investment', 'icon': 'fa-chart-line'},
        {'name': 'Others', 'icon': 'fa-ellipsis'},
    ]
    for cat in default_categories:
        Category.objects.get_or_create(name=cat['name'], defaults={'icon': cat['icon']})

def unload_initial_categories(apps, schema_editor):
    Category = apps.get_model('finance', 'Category')
    Category.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_category_expense_income_monthlybudget'),
    ]

    operations = [
        migrations.RunPython(load_initial_categories, reverse_code=unload_initial_categories),
    ]
