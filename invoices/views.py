from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Invoice, InvoiceItem
from .forms import InvoiceForm
from accounts.mixins import OrganizationPermissionMixin
from .utils import generate_epc_qr_code


class InvoiceListView(LoginRequiredMixin, OrganizationPermissionMixin, ListView):
    model = Invoice
    template_name = 'invoices/invoice_list.html'
    context_object_name = 'invoices'
    
    def get_queryset(self):
        user_orgs = self.get_organizations()
        return Invoice.objects.filter(organization__in=user_orgs).order_by('-issue_date')

class InvoiceCreateView(LoginRequiredMixin, OrganizationPermissionMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoices/invoice_form.html'
    success_url = reverse_lazy('invoices:invoice-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user_orgs = self.get_organizations()
        form.fields['organization'].queryset = user_orgs
        from accounts.models import Contact
        form.fields['contact'].queryset = Contact.objects.filter(organization__in=user_orgs)
        return form

class InvoiceUpdateView(LoginRequiredMixin, OrganizationPermissionMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoices/invoice_form.html'
    success_url = reverse_lazy('invoices:invoice-list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user_orgs = self.get_organizations()
        form.fields['organization'].queryset = user_orgs
        from accounts.models import Contact
        form.fields['contact'].queryset = Contact.objects.filter(organization__in=user_orgs)
        return form
    
    def get_queryset(self):
        user_orgs = self.get_organizations()
        return Invoice.objects.filter(organization__in=user_orgs)

class InvoiceDeleteView(LoginRequiredMixin, OrganizationPermissionMixin, DeleteView):
    model = Invoice
    template_name = 'invoices/invoice_confirm_delete.html'
    success_url = reverse_lazy('invoices:invoice-list')
    
    def get_queryset(self):
        user_orgs = self.get_organizations()
        return Invoice.objects.filter(organization__in=user_orgs)


class InvoicePDFView(LoginRequiredMixin, OrganizationPermissionMixin, DetailView):
    model = Invoice
    template_name = 'invoices/invoice_pdf.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = self.get_object()
        context['qr_code'] = generate_epc_qr_code(
            name=invoice.organization.name,
            iban=invoice.organization.iban,
            amount=invoice.total_amount,
            reference=invoice.reference
        )
        return context

    def render_to_response(self, context, **response_kwargs):
        html_string = render_to_string(self.template_name, context)
        # For local development without C-dependencies, just return the HTML
        # Users can use Cmd+P to "Print to PDF" from the browser.
        return HttpResponse(html_string)