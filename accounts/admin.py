from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Organization, Membership

class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1

class OrganizationAdmin(admin.ModelAdmin):
    inlines = (MembershipInline,)

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Membership)