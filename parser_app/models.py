from django.contrib.postgres.fields import ArrayField
from django.db import models


class Phone(models.Model):
    code = models.CharField(max_length=100, null=True, blank=True)

    title = models.CharField(max_length=255, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    memory = models.CharField(max_length=50, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)

    price = models.FloatField(null=True, blank=True)
    promo_price = models.FloatField(null=True, blank=True)

    screen_diagonal = models.CharField(max_length=50, null=True, blank=True)
    screen_resolution = models.CharField(max_length=50, null=True, blank=True)
    reviews_count = models.IntegerField(null=True, blank=True)

    photos = ArrayField(models.URLField(max_length=500), null=True, blank=True)
    characteristics = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Title: [{self.code}] {self.title}"

    class Meta:
        verbose_name = "Phone"
        verbose_name_plural = "Phones"
