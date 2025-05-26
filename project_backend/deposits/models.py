from django.db import models
from django.contrib.auth import get_user_model

class DepositProduct(models.Model):
    deposit_ID = models.CharField(max_length=20, primary_key=True)  # fin_prdt_cd
    product_type = models.CharField(max_length=10, choices=[('예금', '예금'), ('적금', '적금')])
    
    # 공시 정보
    dcls_month = models.CharField(max_length=6)           # 공시 제출월 (YYYYMM)
    fin_co_no = models.CharField(max_length=20)           # 금융회사 코드
    kor_co_nm = models.CharField(max_length=100)          # 금융회사 명
    fin_prdt_nm = models.CharField(max_length=100)        # 상품명
    
    join_way = models.CharField(max_length=100, blank=True)        # 가입 방법
    mtrt_int = models.CharField(max_length=100, blank=True)        # 만기 후 이자율
    spcl_cnd = models.CharField(max_length=200, blank=True)        # 우대조건
    join_deny = models.CharField(max_length=10, blank=True)        # 가입 제한
    join_member = models.CharField(max_length=200, blank=True)     # 가입 대상
    etc_note = models.TextField(blank=True)                        # 기타 유의사항

    max_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  # 최고한도
    dcls_strt_day = models.CharField(max_length=20, blank=True)    # 공시 시작일
    dcls_end_day = models.CharField(max_length=20, blank=True)     # 공시 종료일
    fin_co_subm_day = models.CharField(max_length=20, blank=True)  # 제출일시 YYYYMMDDHH24MI

    def __str__(self):
        return f"[{self.product_type}] {self.kor_co_nm} - {self.fin_prdt_nm}"


class DepositOption(models.Model):
    depositoption_ID = models.AutoField(primary_key=True)
    deposit = models.ForeignKey(DepositProduct, on_delete=models.CASCADE, related_name='options')

    intr_rate_type = models.CharField(max_length=10)        # 저축 금리 유형 코드
    intr_rate_type_nm = models.CharField(max_length=50)     # 저축 금리 유형 명
    rsrv_type = models.CharField(max_length=10, blank=True) # 적립 유형 코드
    rsrv_type_nm = models.CharField(max_length=50, blank=True) # 적립 유형 명

    save_trm = models.CharField(max_length=10)               # 저축 기간 (개월)
    intr_rate = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)    # 기본 금리
    intr_rate2 = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)   # 최고 우대금리

    def __str__(self):
        return f"{self.deposit.fin_prdt_nm} - {self.save_trm}개월 ({self.intr_rate}%)"


class FavoriteDeposit(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='favorite_deposits')
    deposit = models.ForeignKey(DepositProduct, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'deposit')

    def __str__(self):
        return f"{self.user.username} - {self.deposit.fin_prdt_nm}"
