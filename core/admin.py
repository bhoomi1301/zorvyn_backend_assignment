from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import FinancialRecord, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (*DjangoUserAdmin.fieldsets, ('Role', {'fields': ('role',)}),)
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')


@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'type', 'category', 'date', 'deleted')
    list_filter = ('type', 'category', 'date', 'deleted')
    search_fields = ('user__username', 'category', 'notes')

