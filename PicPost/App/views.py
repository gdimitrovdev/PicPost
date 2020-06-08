from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
#Default django form for creating a user
from django.contrib.auth.forms import UserCreationForm
#Imports needed for creating a new account
from django.contrib.auth import login, authenticate
from .forms import PostForm, ImageForm, SearchForm
from .models import Image, Post
from django.contrib.auth.models import User

#Don't allow user to access the page unless logged in
@login_required
def home(request):
    #Form for the post
    imageform=ImageForm()
    postform=PostForm()
    #database of posts to display
    q=request.user.posts.all()
    for fuser in request.user.getprofile.following.all():
        q=q.union(fuser.posts.all())
    posts=reversed(q.order_by('date'))
    pl=q.count()
    if pl>0:
        p=True
    else:
        p=False
    #pass the username to display
    user=request.user
    #number of posts
    num=len(request.user.posts.all())
    #form to search with
    searchform=SearchForm
    context={'imageform':imageform, 'postform':postform, 'posts':posts, 'user':user, 'num':num, 'searchform':searchform, 'p':p}
    return render(request, 'App/home.html', context)

#Register a new user
def register(request):
    form=UserCreationForm()
    #check if form has been filled
    if request.method=="POST":
        form=UserCreationForm(request.POST)
        if form.is_valid():
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

def profile(request, user_id):
    puser=User.objects.get(pk=user_id)
    my_posts=reversed(puser.posts.all())
    if str(request.user.id)==str(user_id):
        isMine=True
    else:
        isMine = False
    # print(request.user.getprofile.getprofile_set.all())
    context={'posts':my_posts, 'isMine':isMine, 'user_id':user_id}
    return render(request,'App/profile.html',context)

#delete function
def delete(request, post_id, user_id):
    post=Post.objects.get(pk=post_id)
    images=post.images.all()
    for image in images:
        image.delete()
    post.delete()
    return redirect('../../../profile/'+str(user_id))

def searchpost(request):
    form=SearchForm()
    if request.method=="POST":
        form=SearchForm(request.POST)
        if form.is_valid():
            keyword=request.POST['keyword']
            related=reversed(Post.objects.filter(title__contains=keyword))
            context={'related':related}
            return render(request,'App/search.html',context)
    else:
        return redirect('../')

def searchprofile(request):
    form=SearchForm()
    if request.method=="POST":
        form=SearchForm(request.POST)
        if form.is_valid():
            keyword=request.POST['keyword']
            related=User.objects.filter(username__contains=keyword)
            context={'related':related}
            return render(request,'App/searchProfile.html',context)
    else:
        return redirect('../')

def follow(request, id):
    request.user.getprofile.following.add(User.objects.get(pk=id))
    return redirect('../../')