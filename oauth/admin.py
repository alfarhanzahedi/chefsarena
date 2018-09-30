from django.contrib import admin
from .models import UserCodechefAuth

admin.register(UserCodechefAuth)(admin.ModelAdmin)
