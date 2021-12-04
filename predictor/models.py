from __future__ import unicode_literals

from django.db import models


class Prediction(models.Model):
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    square_feet = models.IntegerField()
    condition = models.IntegerField()
    zipcode = models.IntegerField()
    duration = models.IntegerField()
    house_name = models.CharField(max_length=128, null=True)
    principle = models.IntegerField(null=True)
    roi = models.IntegerField(null=True)
    time = models.IntegerField(null=True)
    result = models.CharField(max_length=128)
    customer_id = models.IntegerField()


class Customer(models.Model):
    first_name = models.CharField(max_length=138)
    last_name = models.CharField(max_length=138)
    contact = models.CharField(max_length=64, unique=True)
    address_line1 = models.CharField(max_length=90)
    address_line2 = models.CharField(max_length=90)
    email = models.EmailField(max_length=138, unique=True)

