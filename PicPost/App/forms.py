from django import forms

class ImageForm(forms.Form):
    image = forms.ImageField()

class PostForm(forms.Form):
    title=forms.CharField(max_length=500)