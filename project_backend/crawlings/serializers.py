from rest_framework import serializers
from .models import StockData, UserStockInterest

class StockDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockData
        fields = '__all__'

class UserStockInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStockInterest
        fields = ['id', 'company_name', 'stock_code', 'last_price', 'last_searched', 'created_at']
        read_only_fields = ['id', 'created_at'] 