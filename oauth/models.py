from django.db import models
from django.contrib.auth.models import User

class UserCodechefAuth(models.Model):
    '''
        user: a one-to-one field with Django's in-built User model
        extra_data: a text field to store a users access_token and refresh_token 
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    extra_data = models.TextField()

    def __str__(self):
        return self.user.username