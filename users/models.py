from django.db import models

class SponsoredCustomer(models.Model):
    customer_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.customer_number} - {self.name}"