from django.db import models

class Stock(models.Model):
    symbol = models.CharField(max_length=20)  # 주식 심볼
    name = models.CharField(max_length=100)   # 주식 이름
    current_price = models.DecimalField(max_digits=15, decimal_places=2)  # 현재가
    change = models.DecimalField(max_digits=15, decimal_places=2)  # 변동금액
    change_rate = models.DecimalField(max_digits=10, decimal_places=2)  # 변동률
    volume = models.BigIntegerField()  # 거래량
    timestamp = models.DateTimeField(auto_now=True)  # 데이터 갱신 시간
    ai_analysis = models.TextField(blank=True)  # AI 분석 결과

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.name} ({self.symbol})" 