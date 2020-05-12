from django import forms

class ImageForm(forms.Form):
    image = forms.ImageField(label='')

class PostForm(forms.Form):
    title=forms.CharField(max_length=500, label='', widget=forms.TextInput(attrs={'class':'postInput'}))

class SearchPostForm(forms.Form):
    keyword=forms.CharField(max_length=500, label='', widget=forms.TextInput(attrs={'class':'postInput'}))