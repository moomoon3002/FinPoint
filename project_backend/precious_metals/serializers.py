from rest_framework import serializers
from .models import MetalPrice

class MetalPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetalPrice
        fields = ['metal_type', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']

class MetalPriceUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    metal_type = serializers.ChoiceField(choices=MetalPrice.METAL_TYPES) 