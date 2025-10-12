from django.urls import path
from .views import InvoiceListView, InvoicePDFView

app_name = 'invoices'

urlpatterns = [
    path('', InvoiceListView.as_view(), name='invoice-list'),
    path('<int:pk>/pdf/', InvoicePDFView.as_view(), name='invoice-pdf'),
]