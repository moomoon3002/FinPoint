from rest_framework import serializers
from .models import Stock

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['symbol', 'name', 'current_price', 'change', 'change_rate', 'volume', 'timestamp', 'ai_analysis'] 