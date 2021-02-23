# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from .forms import PostForm, ImageForm, SearchForm
from .models import Image, Post, Message
from django.contrib.auth.models import User
from django.http import JsonResponse

# Don't allow user to access the page unless logged in
@login_required
def home(request):
    # Form for the post
    imageform = ImageForm()
    postform = PostForm()

    # database of posts to display
    q=request.user.posts.all()
    for fuser in request.user.getprofile.following.all():
        q=q.union(fuser.posts.all())
    posts=reversed(q.order_by('date'))
    pl=q.count()
    if pl>0:
        p=True
    else:
        p=False

    # pass the username
    user=request.user

    #number of posts
    num=len(request.user.posts.all())

    #form to search with
    searchform=SearchForm

    context={'imageform':imageform,
             'postform':postform,
             'posts':posts,
             'user':user,
             'num':num,
             'searchform':searchform,
             'p':p}
    return render(request, 'app/home.html', context)

# Register a new user
def register(request):
    form=UserCreationForm()
    # check if form has been filled
    if request.method=="POST":
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Get provided username and password
            username=form.cleaned_data['username']
            password=form.cleaned_data['password1']
            user=authenticate(username=username, password=password)
            login(request, user)
            # if form is filled in redirect to homepage
            return redirect('../')
    # if form is not filled display the form
    context={'form':form}
    return render(request, 'registration/register.html', context)

def addpost(request):
    imageform=ImageForm()
    postform=PostForm()
    if request.method=="POST":
        imageform=ImageForm(request.POST, request.FILES)
        postform=PostForm(request.POST)
        if imageform.is_valid() and postform.is_valid():
            # add the image and the post to the database
            image=Image(image=request.FILES['image'])
            image.save()
            title=request.POST['title']
            post=Post(title=title, user=request.user)
            post.save()
            post.images.add(image)
    return redirect('../')

def profile(request, user_id):
    # get the user whose profile we are watching
    puser=User.objects.get(pk=user_id)

    # check if we are following him
    isFollowed=False
    if puser in request.user.getprofile.following.all():
        isFollowed=True

    # get the user's latests posts
    my_posts=reversed(puser.posts.all())

    # check if the user whose profile is loaded is the same as the authenticated user
    if str(request.user.id)==str(user_id):
        isMine=True
    else:
        isMine = False

    # get the user's username
    name=puser.username

    # check how many followers does the user have
    followersNum=puser.followed_by.all().count()

    context={'posts':my_posts,
             'isMine':isMine,
             'user_id':user_id,
             'isFollowed':isFollowed,
             'fn':followersNum,
             'name':name}
    return render(request,'app/profile.html',context)

# delete function
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
            return render(request,'app/search.html',context)
    else:
        return redirect('../')

def searchprofile(request):
    form=SearchForm()
    if request.method=="POST":
        form=SearchForm(request.POST)
        if form.is_valid():
            keyword=request.POST['keyword']
            users=User.objects.filter(username__contains=keyword).exclude(pk=request.user.id)
            isFollowed=[]
            for u in users:
                if u in request.user.getprofile.following.all():
                    isFollowed.append(True)
                else:
                    isFollowed.append(False)
            related=zip(users,isFollowed)
            context={'related':related}
            return render(request,'app/searchProfile.html',context)
    else:
        return redirect('../')

def follow(request, id):
    request.user.getprofile.following.add(User.objects.get(pk=id))
    return redirect('../../')

def unfollow(request, id):
    request.user.getprofile.following.remove(User.objects.get(pk=id))
    return redirect('../../')

def changeurl(request, id):
    # s will be the string of the generated url
    s=''

    # get the ids of the users that will be chatting
    id1=int(request.user.id)
    id2=int(id)

    # create the url
    if id1<id2:
        s=str(id1)+'_'+str(id2)
    else:
        s = str(id2) + '_' + str(id1)

    # send the users to the chat url
    return redirect('../../chat/'+s)

# this is the chat url
def chat(request, room_name):
    ids=room_name.split('_')
    if str(request.user.id) not in ids:
        return redirect('../../')
    return render(request,'app/chat.html',{'room_name':room_name})

# this is an ajax call to preload the last 50 messages between the two users
def get_msg(request):
    room=request.GET.get('room', None)
    messages=Message.objects.filter(room=room).order_by('date')[:50]
    data={}
    fakeData=[]
    for msg in messages:
        fakeData.append([msg.sender.username,msg.text])
    data[0]=fakeData
    return JsonResponse(data)

# this function loads all conversations that the user has participated in
def messages(request):
    last = {}

    # get the messages that the user has sent
    messages_sent=Message.objects.filter(sender=request.user).order_by("date")

    # get the last sent message to every user
    for msg in messages_sent:
        if msg.rec in last:
            last[msg.rec].append(msg)
        else:
            last[msg.rec]=[msg]
    for key in last:
        last[key]=last[key][-1]

    # get the messages that the user has received and if he has responded check the date
    messages_rec=Message.objects.filter(rec=request.user).order_by("date")
    for msg in messages_rec:
        if msg.sender in last:
            if msg.date>=last[msg.sender].date:
                last[msg.sender]=msg
        else:
            last[msg.sender]=msg

    # sort all the messages by date
    listofTuples = sorted(last.items(), key=lambda x: x[1].date)[::-1]

    # search form to search for other users to chat with
    searchform=SearchForm()

    context={'last':listofTuples, 'searchform':searchform}
    return render(request, 'app/messages.html', context)