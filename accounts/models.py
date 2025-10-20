# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('owner', 'Pet Owner'),
        ('customer', 'Customer'),
        ('vet', 'Vet'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'  # login with email
    REQUIRED_FIELDS = ['username']  # username still required for Django

    def __str__(self):
        return self.email
