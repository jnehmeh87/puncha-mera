from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from accounts.mixins import OrganizationPermissionMixin
from .models import Expense, Income
import google.generativeai as genai
import os
import json

class LedgerView(LoginRequiredMixin, OrganizationPermissionMixin, ListView):
    template_name = 'bookkeeping/ledger.html'
    context_object_name = 'transactions'
    
    def get_queryset(self):
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_orgs = self.get_organizations()
        context['expenses'] = Expense.objects.filter(organization__in=user_orgs).order_by('-date_incurred')
        context['incomes'] = Income.objects.filter(organization__in=user_orgs).order_by('-bank_registry_date')
        return context

class ParseReceiptView(LoginRequiredMixin, OrganizationPermissionMixin, View):
    def post(self, request, *args, **kwargs):
        if 'receipt' not in request.FILES:
            return JsonResponse({'error': 'No receipt image provided'}, status=400)
            
        receipt_file = request.FILES['receipt']
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return JsonResponse({'error': 'GEMINI_API_KEY not configured. Contact admin.'}, status=501)
            
        genai.configure(api_key=api_key)
        
        try:
            from PIL import Image
            img = Image.open(receipt_file)
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = """
            Analyze this receipt or invoice and return ONLY a raw JSON object (no markdown formatting, no backticks) with the following keys:
            - vendor: The name of the merchant or company.
            - date: The date of the transaction in YYYY-MM-DD format. Return empty string if not found.
            - amount: The total numerical amount as a float/decimal.
            - currency: The 3-letter currency code if found (e.g. USD, EUR, SEK). Defaults to USD if strictly unknown.
            """
            response = model.generate_content([prompt, img])
            
            content_text = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(content_text)
            
            return JsonResponse(data)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ExpenseCreateView(LoginRequiredMixin, OrganizationPermissionMixin, CreateView):
    model = Expense
    fields = ['organization', 'amount', 'currency', 'date_incurred', 'payment_date', 'vendor', 'description', 'receipt_image']
    template_name = 'bookkeeping/expense_form.html'
    success_url = '/bookkeeping/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organizations'] = self.get_organizations()
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['organization'].queryset = self.get_organizations()
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class IncomeCreateView(LoginRequiredMixin, OrganizationPermissionMixin, CreateView):
    model = Income
    fields = ['organization', 'amount', 'currency', 'bank_registry_date', 'source', 'invoice', 'description']
    template_name = 'bookkeeping/income_form.html'
    success_url = '/bookkeeping/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organizations'] = self.get_organizations()
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['organization'].queryset = self.get_organizations()
        # Also potentially filter invoice choices if needed
        from invoices.models import Invoice
        form.fields['invoice'].queryset = Invoice.objects.filter(organization__in=self.get_organizations())
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
