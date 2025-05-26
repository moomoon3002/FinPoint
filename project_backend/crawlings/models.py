from django.db import models
import json

class StockData(models.Model):
    company_name = models.CharField(max_length=100)
    stock_code = models.CharField(max_length=10)
    comments = models.TextField()
    analysis = models.TextField()
    price_info = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company_name} ({self.stock_code})" 