from django.db import models
from django.contrib.auth import get_user_model
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

class UserStockInterest(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='interested_stocks')
    company_name = models.CharField(max_length=100)
    stock_code = models.CharField(max_length=10)
    last_price = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    last_searched = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_searched']
        unique_together = ['user', 'stock_code']  # 한 사용자가 같은 주식을 중복해서 저장하지 않도록

    def __str__(self):
        return f"{self.user.username} - {self.company_name} ({self.stock_code})" 