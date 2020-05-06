from django.db import models
import uuid
from django.contrib.auth import get_user_model

class Image(models.Model):
    image=models.ImageField(upload_to='postimages')
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)

class Post(models.Model):
    title=models.CharField(max_length=500)
    created_date=models.DateField(auto_now=True)
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    images=models.ManyToManyField(Image)
    user=models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, related_name='posts')