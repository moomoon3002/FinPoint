from rest_framework import serializers
from .models import DepositProduct, DepositOption

class DepositOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositOption
        fields = ['save_trm', 'intr_rate_type', 'intr_rate_type_nm', 
                 'rsrv_type', 'rsrv_type_nm', 'intr_rate', 'intr_rate2']

class DepositProductSerializer(serializers.ModelSerializer):
    options = DepositOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = DepositProduct
        fields = ['deposit_ID', 'product_type', 'dcls_month', 'fin_co_no', 
                 'kor_co_nm', 'fin_prdt_nm', 'join_way', 'mtrt_int', 
                 'spcl_cnd', 'join_deny', 'join_member', 'etc_note', 
                 'max_limit', 'dcls_strt_day', 'dcls_end_day', 
                 'fin_co_subm_day', 'options']