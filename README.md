# ExpenseTracker Pro (FinAlytica)

ExpenseTracker Pro is a production-quality personal finance, budgeting, and spending analytics dashboard application built using Django, SQLite, Bootstrap 5, and Chart.js. 

This project incorporates database transaction safety, 3-month Simple Moving Average spending forecasting, and visual analytical insights designed for software engineering portfolios.

---

## Key Features

- **Robust Authentication & Profile Management**: Complete secure registration, login, logout, and profile management including customizable preferred base currencies.
- **Transactional CRUD (Atomicity)**: Income and expense tracking pages with search capabilities, category classifications, and date range filters. All database modifications are secured using Django's `transaction.atomic()` to guarantee bookkeeping integrity.
- **Visual Analytics Dashboard (Chart.js)**:
  - *Daily Expense Trend*: Line chart showing daily spending trends in the current month.
  - *Category Breakdown*: Doughnut chart mapping expenses by category.
  - *Monthly Balance Tracker*: Comparative bar chart showing Income vs Expenses over the past 6 months.
- **Quantitative Budget Forecasting (SMA)**: Simple Moving Average calculation based on the previous three months of spending to predict current month total outlays, triggering warnings if projected expenditures exceed budget caps.
- **CSV Data Exporter**: Quick utility allowing users to download their entire expense logs history as a formatted `.csv` spreadsheet.

---

## Technology Stack

- **Backend**: Python 3, Django 4.2+ (MVC architecture with modular service layers)
- **Database**: SQLite (SQL Relational Database)
- **Frontend CSS**: Bootstrap 5 (Responsive Layout, custom Dark Fintech styling)
- **Data Visualizations**: Chart.js (HTML5 Canvas Charts)
- **Client Scripting**: Vanilla JavaScript
- **Environment**: Python-dotenv (Secure environment variables manager)

---

## Directory Structure

```text
ExpenseTrackerPro/
│
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
│
├── expensetracker/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── finance/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   ├── services.py   # Forecasting and budget algorithms
│   ├── utils.py      # CSV exporter utilities
│   ├── tests.py      # Test suite
│   └── migrations/
│
└── templates/
    ├── base.html
    ├── registration/
    │   ├── login.html
    │   └── register.html
    └── finance/
        ├── dashboard.html
        ├── income_list.html
        ├── expense_list.html
        └── profile.html
```

---

## Installation & Setup

### Prerequisites
- Python 3.10 or higher installed.

### Steps
1. **Clone or Download the Project**:
   Ensure you place it in a separate directory (e.g. `C:/Users/.../Downloads/ExpenseTrackerPro`).

2. **Set up virtual environment (Optional but recommended)**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables**:
   Create a `.env` file at the root by copying `.env.example` and filling in the values:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. **Apply Database Migrations**:
   ```bash
   python manage.py migrate
   ```
   *(Note: This will automatically seed the initial categories into the database!)*

6. **Create Admin Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**:
   Start the server on port 8080:
   ```bash
   python manage.py runserver 8080
   ```

8. **Run Tests**:
   Run the test runner to verify everything is solid:
   ```bash
   python manage.py test
   ```

---

## Future Enhancements
- **Multi-currency API Integration**: Fetching real-time exchange rates dynamically.
- **PDF Report Exporters**: Generate print-friendly monthly spending summaries.
- **Email Alert Digests**: Weekly budget recap messages sent automatically to users.
