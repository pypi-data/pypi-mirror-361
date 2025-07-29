from django.db import models


class MomotorToken(models.Model):
    api_key = models.CharField(max_length=100, primary_key=True)
    token = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
