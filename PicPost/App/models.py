from django.db import models
import uuid
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
import datetime

class Image(models.Model):
    image=models.ImageField(upload_to='postimages')
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)

class Post(models.Model):
    title=models.CharField(max_length=500)
    created_date=models.DateField(auto_now=True)
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    images=models.ManyToManyField(Image)
    user=models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, related_name='posts')
    date=models.DateField(auto_now_add=True)

class Profile(models.Model):
    user=models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True, related_name='getprofile')
    following=models.ManyToManyField(get_user_model(), related_name='followed_by')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.getprofile.save()