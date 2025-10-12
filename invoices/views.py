from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Invoice
from projects.mixins import OrganizationPermissionMixin
from .utils import generate_epc_qr_code


class InvoiceListView(LoginRequiredMixin, OrganizationPermissionMixin, ListView):
    model = Invoice
    template_name = 'invoices/invoice_list.html'
    context_object_name = 'invoices'


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
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{self.object.invoice_number}.pdf"'
        return response