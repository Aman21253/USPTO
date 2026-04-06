from django.db import models

class PatentApplication(models.Model):
    application_number = models.CharField(max_length=50, unique=True)
    customer_number = models.CharField(max_length=50)
    title = models.CharField(max_length=255, blank=True, null=True)
    priority = models.BooleanField(default=False)

    def __str__(self):
        return self.application_number


class PatentDocument(models.Model):
    application = models.ForeignKey(PatentApplication, on_delete=models.CASCADE)
    document_code = models.CharField(max_length=50)
    mailroom_date = models.DateField()

    class Meta:
        unique_together = ("application", "document_code", "mailroom_date")

    def __str__(self):
        return f"{self.application.application_number} - {self.document_code}"