# Generated by Django 4.2.16 on 2025-05-25 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MetalPrice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "metal_type",
                    models.CharField(
                        choices=[("GOLD", "금"), ("SILVER", "은")],
                        max_length=10,
                        verbose_name="금속 종류",
                    ),
                ),
                ("date", models.DateField(verbose_name="날짜")),
                (
                    "close_price",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="종가"
                    ),
                ),
                ("volume", models.BigIntegerField(verbose_name="거래량")),
                (
                    "open_price",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="시가"
                    ),
                ),
                (
                    "high_price",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="고가"
                    ),
                ),
                (
                    "low_price",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="저가"
                    ),
                ),
            ],
            options={
                "verbose_name": "금속 가격",
                "verbose_name_plural": "금속 가격들",
                "ordering": ["-date"],
                "unique_together": {("metal_type", "date")},
            },
        ),
    ]
