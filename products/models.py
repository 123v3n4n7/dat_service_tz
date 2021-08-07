from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, null=False)
    href = models.TextField(null=False, default='')

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False)
    price = models.CharField(max_length=100, null=False)
    image = models.ImageField(upload_to='products_images')

    def __str__(self):
        return self.name
