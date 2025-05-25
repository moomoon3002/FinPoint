from django.contrib import admin
from .models import DepositProduct, DepositOption

class DepositOptionInline(admin.TabularInline):
    model = DepositOption
    extra = 1

@admin.register(DepositProduct)
class DepositProductAdmin(admin.ModelAdmin):
    list_display = ('deposit_ID', 'product_name', 'product_bank', 'highest_interest_rate')
    inlines = [DepositOptionInline]

    # 상품명
    def product_name(self, obj):
        return obj.fin_prdt_nm

    # 금융회사명
    def product_bank(self, obj):
        return obj.kor_co_nm

    # 최고 우대금리 계산 (연결된 옵션 중 최댓값)
    def highest_interest_rate(self, obj):
        highest = obj.options.aggregate(models.Max('intr_rate2'))['intr_rate2__max']
        return f"{highest:.2f}%" if highest is not None else "-"
