# make_superuser.py
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')  # replace Backend with your project name
django.setup()

from accounts.models import User

# Update user
user = User.objects.get(email="powsadmin@gmail.com")
user.is_staff = True
user.is_superuser = True
user.save()

print("User is now a superuser/staff!")
