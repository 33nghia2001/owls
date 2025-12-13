"""
Vendors Admin Configuration for Owls E-commerce Platform
========================================================
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Vendor, VendorDocument, VendorBankAccount, VendorPayout


class VendorDocumentInline(admin.TabularInline):
    model = VendorDocument
    extra = 0


class VendorBankAccountInline(admin.TabularInline):
    model = VendorBankAccount
    extra = 0


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = [
        'store_name', 'owner', 'status', 'rating',
        'total_products', 'total_orders', 'total_sales', 'created_at'
    ]
    list_filter = ['status', 'is_active', 'is_verified', 'created_at']
    search_fields = ['store_name', 'owner__email', 'business_email', 'tax_code']
    raw_id_fields = ['owner']
    readonly_fields = [
        'id', 'slug', 'total_products', 'total_orders', 'total_sales',
        'rating', 'total_reviews', 'created_at'
    ]
    inlines = [VendorDocumentInline, VendorBankAccountInline]

    actions = ['approve_vendors', 'suspend_vendors']

    @admin.action(description='Approve selected vendors')
    def approve_vendors(self, request, queryset):
        queryset.update(status='approved', is_active=True)

    @admin.action(description='Suspend selected vendors')
    def suspend_vendors(self, request, queryset):
        queryset.update(status='suspended', is_active=False)


@admin.register(VendorDocument)
class VendorDocumentAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'document_type', 'is_verified', 'created_at']
    list_filter = ['document_type', 'is_verified']
    search_fields = ['vendor__store_name']
    raw_id_fields = ['vendor']


@admin.register(VendorBankAccount)
class VendorBankAccountAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'bank_name', 'account_number', 'is_default', 'is_verified']
    list_filter = ['bank_name', 'is_verified', 'is_default']
    search_fields = ['vendor__store_name', 'account_holder_name']
    raw_id_fields = ['vendor']


@admin.register(VendorPayout)
class VendorPayoutAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'amount', 'status', 'created_at', 'processed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['vendor__store_name']
    raw_id_fields = ['vendor', 'bank_account']
    readonly_fields = ['created_at']
