from django.db import models

# Create your models here.


class APIKeyHandel(models.Model):
    api_key = models.CharField(max_length=100)
    is_live = models.BooleanField(default=False)

    def __str__(self):
        return self.api_key
    
    