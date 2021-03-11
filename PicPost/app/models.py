# stdlib imports
import uuid

# Django imports
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


# database for the images
class Image(models.Model):
    image = models.ImageField(upload_to='postimages')
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)


# database for the posts (with ManyToMany relation to Images)
class Post(models.Model):
    title = models.CharField(max_length=500)
    created_date = models.DateField(auto_now=True)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    images = models.ManyToManyField(Image)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, related_name='posts')
    date = models.DateField(auto_now_add=True)


# OneToOneField to the User model made to implement the following functionality
class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True, related_name='getprofile')
    following = models.ManyToManyField(get_user_model(), related_name='followed_by')


# update the Profile based on the user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.getprofile.save()


# database that contains the previously sent messages
class Message(models.Model):
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, related_name='sent')
    rec = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, related_name='recieved')
    text = models.CharField(max_length=400)
    date = models.DateTimeField(auto_now_add=True)
    room = models.CharField(max_length=20000)
