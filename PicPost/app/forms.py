# Django imports
from django import forms

# form to add a picture to the post
class ImageForm(forms.Form):
    image = forms.ImageField(label='Picture:')

# form for the text in the post
class PostForm(forms.Form):
    title=forms.CharField(max_length=500, label='Caption:', widget=forms.TextInput(attrs={'class':'postInput'}))

# form used to search for users and posts
class SearchForm(forms.Form):
    keyword=forms.CharField(max_length=500, label='', widget=forms.TextInput(attrs={'class':'postInput'}))