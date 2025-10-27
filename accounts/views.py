from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import FormView, View, ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.urls import reverse, reverse_lazy
from allauth.account.views import SignupView
from .forms import InvitationForm, OrganizationForm
from .models import Invitation, Organization, CustomUser, Membership, Contact
from .mixins import OrganizationPermissionMixin, AdminOwnerRequiredMixin

class SendInvitationView(LoginRequiredMixin, AdminOwnerRequiredMixin, FormView):
    template_name = 'accounts/send_invitation.html'
    form_class = InvitationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = Organization.objects.get(pk=self.kwargs['organization_pk'])
        return context

    def form_valid(self, form):
        email = form.cleaned_data['email']
        role = form.cleaned_data['role']
        organization = Organization.objects.get(pk=self.kwargs['organization_pk'])

        invitation = Invitation.objects.create(
            email=email,
            organization=organization,
            role=role
        )

        invitation_link = self.request.build_absolute_uri(
            reverse('accounts:accept-invitation', kwargs={'token': invitation.token})
        )

        send_mail(
            'You have been invited to join an organization',
            f'Click the link to accept the invitation: {invitation_link}',
            'from@example.com',
            [email],
            fail_silently=False,
        )

        return redirect('home:home')

class AcceptInvitationView(View):
    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        try:
            invitation = Invitation.objects.get(token=token)
        except Invitation.DoesNotExist:
            # Handle invalid token
            return redirect('home:home')

        request.session['invitation_token'] = str(invitation.token)
        return redirect('account_signup')

class CustomSignupView(SignupView):
    def form_valid(self, form):
        response = super().form_valid(form)
        invitation_token = self.request.session.get('invitation_token')
        if invitation_token:
            try:
                invitation = Invitation.objects.get(token=invitation_token)
                user = self.user
                organization = invitation.organization
                role = invitation.role
                Membership.objects.create(user=user, organization=organization, role=role)
                invitation.delete()
                del self.request.session['invitation_token']
            except Invitation.DoesNotExist:
                pass
        return response

class OrganizationListView(LoginRequiredMixin, ListView):
    model = Organization
    template_name = 'accounts/organization_list.html'

    def get_queryset(self):
        return Organization.objects.filter(members__user=self.request.user, deleted=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['active_organizations'] = queryset.filter(archived=False)
        context['archived_organizations'] = queryset.filter(archived=True)
        return context

class OrganizationDetailView(LoginRequiredMixin, DetailView):
    model = Organization
    template_name = 'accounts/organization_detail.html'

class OrganizationCreateView(LoginRequiredMixin, CreateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'accounts/organization_form.html'
    success_url = reverse_lazy('accounts:organization-list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        Membership.objects.create(user=self.request.user, organization=self.object, role='owner')
        return response

class ContactListView(OrganizationPermissionMixin, ListView):
    model = Contact
    template_name = 'accounts/contact_list.html'

    def get_queryset(self):
        user = self.request.user
        try:
            membership = Membership.objects.get(user=user)
            organization = membership.organization
            return Contact.objects.filter(organization=organization, deleted=False)
        except Membership.DoesNotExist:
            return Contact.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['active_contacts'] = queryset.filter(archived=False)
        context['archived_contacts'] = queryset.filter(archived=True)
        return context

class ContactDetailView(OrganizationPermissionMixin, DetailView):
    model = Contact
    template_name = 'accounts/contact_detail.html'

class ContactCreateView(OrganizationPermissionMixin, CreateView):
    model = Contact
    fields = ['name', 'contact_type', 'company_email', 'company_address', 'company_contact_person']
    template_name = 'accounts/contact_form.html'
    success_url = reverse_lazy('accounts:contact-list')

    def form_valid(self, form):
        user = self.request.user
        try:
            membership = Membership.objects.get(user=user)
            organization = membership.organization
            form.instance.organization = organization
        except Membership.DoesNotExist:
            form.add_error(None, "You are not a member of any organization. Please create or join an organization first.")
            return super().form_invalid(form)
        return super().form_valid(form)

class ContactUpdateView(OrganizationPermissionMixin, UpdateView):
    model = Contact
    fields = ['name', 'contact_type', 'company_email', 'company_address', 'company_contact_person']
    template_name = 'accounts/contact_form.html'
    success_url = reverse_lazy('accounts:contact-list')

class ContactDeleteView(OrganizationPermissionMixin, DeleteView):
    model = Contact
    template_name = 'accounts/contact_confirm_delete.html'
    success_url = reverse_lazy('accounts:contact-list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.deleted = True
        self.object.save()
        return redirect(self.get_success_url())

def archive_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.archived = True
    contact.save()
    return redirect('accounts:contact-list')

def unarchive_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.archived = False
    contact.save()
    return redirect('accounts:contact-list')

def archive_organization(request, pk):
    organization = get_object_or_404(Organization, pk=pk)
    organization.archived = True
    organization.save()
    return redirect('accounts:organization-list')

def unarchive_organization(request, pk):
    organization = get_object_or_404(Organization, pk=pk)
    organization.archived = False
    organization.save()
    return redirect('accounts:organization-list')