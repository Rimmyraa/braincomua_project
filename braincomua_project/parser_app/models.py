from django.db import models


class Product(models.Model):

    # Product info
    title = models.CharField(max_length=500, null=True, blank=True)
    manufacturer = models.CharField(max_length=100, null=True, blank=True)
    product_code = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    memory = models.CharField(max_length=50, null=True, blank=True)

    # Prices
    price = models.IntegerField(null=True, blank=True)
    sale_price = models.IntegerField(null=True, blank=True)

    # Screen
    screen_diagonal = models.CharField(max_length=50, null=True, blank=True)
    screen_resolution = models.CharField(max_length=50, null=True, blank=True)

    # Reviews
    reviews_count = models.IntegerField(null=True, blank=True)

    # Images and specifications
    images = models.JSONField(null=True, blank=True)
    specifications = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.title or ''

    class Meta:
        verbose_name = 'Product'