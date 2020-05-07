from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
#Default django form for creating a user
from django.contrib.auth.forms import UserCreationForm
#Imports needed for creating a new account
from django.contrib.auth import login, authenticate
from .forms import PostForm, ImageForm
from .models import Image, Post

#Don't allow user to access the page unless logged in
@login_required
def home(request):
    #Form for the post
    imageform=ImageForm()
    postform=PostForm()
    #database of posts to display
    posts=reversed(Post.objects.all())
    #pass the username to display
    user=request.user
    #number of posts
    num=len(request.user.posts.all())
    context={'imageform':imageform, 'postform':postform, 'posts':posts, 'user':user, 'num':num}
    return render(request, 'App/home.html', context)

#Register a new user
def register(request):
    form=UserCreationForm()
    #check if form has been filled
    if request.method=="POST":
        form=UserCreationForm(request.POST)
        if form.is_valid:
            form.save()
            #Get provided username and password
            username=form.cleaned_data['username']
            password=form.cleaned_data['password1']
            user=authenticate(username=username, password=password)
            login(request, user)
            #if form is filled in redirect to homepage
            return redirect('../')
    #if form is not filled display the form
    context={'form':form}
    return render(request, 'registration/register.html', context)

def addpost(request):
    imageform=ImageForm()
    postform=PostForm()
    if request.method=="POST":
        imageform=ImageForm(request.POST, request.FILES)
        postform=PostForm(request.POST)
        if imageform.is_valid() and postform.is_valid():
            #add the image and the post to the database
            image=Image(image=request.FILES['image'])
            image.save()
            title=request.POST['title']
            post=Post(title=title, user=request.user)
            post.save()
            post.images.add(image)
    return redirect('../')

def profile(request):
    my_posts=reversed(request.user.posts.all())
    context={'posts':my_posts}
    return render(request,'App/profile.html',context)

#delete function
def delete(request, post_id):
    post=Post.objects.get(pk=post_id)
    images=post.images.all()
    for image in images:
        image.delete()
    post.delete()
    return redirect('../../profile')


