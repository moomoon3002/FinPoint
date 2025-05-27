from django.db import models
from django.conf import settings

class IPOEvent(models.Model):
    company_name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=50)  # 청약, 상장 등
    event_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['event_date']

    def __str__(self):
        return f"{self.company_name} - {self.event_type} ({self.event_date})"

class UserIPOInterest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ipo_event = models.ForeignKey(IPOEvent, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'ipo_event']

    def __str__(self):
        return f"{self.user.username} - {self.ipo_event.company_name}" 