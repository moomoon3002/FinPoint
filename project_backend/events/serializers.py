from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'time', 'color']
        read_only_fields = ['id']

    def create(self, validated_data):
        # 현재 로그인한 사용자를 이벤트 소유자로 설정
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data) 