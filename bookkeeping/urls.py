from django.urls import path
from . import views

app_name = 'bookkeeping'

urlpatterns = [
    path('', views.LedgerView.as_view(), name='ledger'),
    path('expenses/create/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('expenses/parse-receipt/', views.ParseReceiptView.as_view(), name='parse_receipt'),
    path('incomes/create/', views.IncomeCreateView.as_view(), name='income_create'),
]
