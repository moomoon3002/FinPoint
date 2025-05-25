from django.db import models

# Create your models here.

class MetalPrice(models.Model):
    METAL_TYPES = [
        ('GOLD', '금'),
        ('SILVER', '은'),
    ]
    
    metal_type = models.CharField(max_length=10, choices=METAL_TYPES)
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.IntegerField()
    
    class Meta:
        unique_together = ['metal_type', 'date']
        ordering = ['date']  # 날짜순 정렬
    
    def __str__(self):
        return f"{self.metal_type} - {self.date}"
