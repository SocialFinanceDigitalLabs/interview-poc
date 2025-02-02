from django.db import models

# Create your models here.




class Person(models.Model): 

    external_id = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    'used gender_choices to ensure valid data and improves readability, it ensures only valid gender values are entered'
    GENDER_CHOICES = [
        ('male','Male'),
        ('female','Female'),
        ('other','Other'),
        ('prefer not to say','Prefer not to say')
    ]
    gender = models.CharField(max_length = 30,choices=GENDER_CHOICES, null = True, blank = True)
    region = models.CharField(max_length = 50, null = True, blank = True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} - {self.date_of_birth}'