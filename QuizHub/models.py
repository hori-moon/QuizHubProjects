# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    supabase_user_id = models.UUIDField(null=True, blank=True, unique=True)
