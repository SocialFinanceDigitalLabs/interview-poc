from django.db import models

class Person(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20)
    region = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.id
    
