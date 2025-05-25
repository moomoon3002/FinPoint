from rest_framework import viewsets, permissions
from .models import Event
from .serializers import EventSerializer

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 현재 로그인한 사용자의 이벤트만 반환
        return Event.objects.filter(user=self.request.user) 