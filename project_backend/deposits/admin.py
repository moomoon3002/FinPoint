from django.contrib import admin
from .models import DepositProduct, DepositOption

class DepositOptionInline(admin.TabularInline):
    model = DepositOption
    extra = 1

@admin.register(DepositProduct)
class DepositProductAdmin(admin.ModelAdmin):
    list_display = ('deposit_ID', 'product_name', 'product_bank', 'highest_interst_rate')
    inlines = [DepositOptionInline]

admin.site.register(DepositOption)