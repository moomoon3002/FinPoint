from django.db import models

class MetalPrice(models.Model):
    METAL_TYPES = [
        ('GOLD', '금'),
        ('SILVER', '은'),
    ]
    
    metal_type = models.CharField(max_length=10, choices=METAL_TYPES)
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    high_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    low_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    close_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    volume = models.DecimalField(max_digits=10, decimal_places=3, null=True)  # 소수점까지 고려

    class Meta:
        unique_together = ['metal_type', 'date']
        ordering = ['date']
    
    def __str__(self):
        return f"{self.metal_type} - {self.date}"