# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from .forms import PostForm, ImageForm, SearchForm
from .models import Image, Post, Message, Comment
from django.contrib.auth.models import User
from django.http import JsonResponse


# Don't allow user to access the page unless logged in
@login_required
def home(request):
    # Form for the post
    imageform = ImageForm()
    postform = PostForm()

    # database of posts to display
    q = request.user.posts.all()
    for fuser in request.user.getprofile.following.all():
        q = q.union(fuser.posts.all())
    posts = reversed(q.order_by('date'))
    posts_l = q.count()
    if posts_l > 0:
        any_posts = True
    else:
        any_posts = False

    # pass the username
    user = request.user

    # number of posts by the user
    num = len(request.user.posts.all())

    # form to search with
    searchform = SearchForm

    context = {'imageform': imageform,
               'postform': postform,
               'posts': posts,
               'user': user,
               'num': num,
               'searchform': searchform,
               'p': any_posts
               }
    return render(request, 'app/home.html', context)


# Register a new user
def register(request):
    form = UserCreationForm()
    # check if form has been filled
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Get provided username and password
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            # if form is filled in redirect to homepage
            return redirect('../')
    # if form is not filled display the form
    context = {'form': form}
    return render(request, 'registration/register.html', context)


@login_required
def addpost(request):
    imageform = ImageForm()
    postform = PostForm()
    if request.method == "POST":
        imageform = ImageForm(request.POST, request.FILES)
        postform = PostForm(request.POST)
        if imageform.is_valid() and postform.is_valid():
            # add the image and the post to the database
            image = Image(image=request.FILES['image'])
            image.save()
            title = request.POST['title']
            post = Post(title=title, user=request.user)
            post.save()
            post.images.add(image)
    return redirect('../')


@login_required
def profile(request, user_id):
    # get the user whose profile we are watching
    puser = User.objects.get(pk=user_id)

    # check if we are following him
    is_followed = False
    if puser in request.user.getprofile.following.all():
        is_followed = True

    # get the user's latest posts
    posts = reversed(puser.posts.all())

    # check if the user whose profile is loaded is the same as the authenticated user
    if str(request.user.id) == str(user_id):
        is_mine = True
    else:
        is_mine = False

    # get the user's username
    name = puser.username

    # check how many followers does the user have
    followers_num = puser.followed_by.all().count()

    context = {'posts': posts,
               'isMine': is_mine,
               'user_id': user_id,
               'isFollowed': is_followed,
               'fn': followers_num,
               'name': name,
               }
    return render(request, 'app/profile.html', context)


@login_required
# delete function
def delete(request, post_id, user_id):
    post = Post.objects.get(pk=post_id)
    images = post.images.all()
    for image in images:
        image.delete()
    post.delete()
    return redirect('../../../profile/'+str(user_id))


@login_required
def searchpost(request):
    form = SearchForm()
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            keyword = request.POST['keyword']
            related = reversed(Post.objects.filter(title__contains=keyword))
            context = {'related': related}
            return render(request, 'app/search.html', context)
    else:
        return redirect('../')


@login_required
def searchprofile(request):
    form = SearchForm()
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            keyword = request.POST['keyword']
            users = User.objects.filter(username__contains=keyword).exclude(pk=request.user.id)
            is_followed = []
            for u in users:
                if u in request.user.getprofile.following.all():
                    is_followed.append(True)
                else:
                    is_followed.append(False)
            related = zip(users, is_followed)
            context = {'related': related}
            return render(request, 'app/searchProfile.html', context)
    else:
        return redirect('../')


@login_required
def follow(request, id):
    request.user.getprofile.following.add(User.objects.get(pk=id))
    return redirect('../../')


@login_required
def unfollow(request, id):
    request.user.getprofile.following.remove(User.objects.get(pk=id))
    return redirect('../../')


@login_required
def changeurl(request, id):
    # s will be the string of the generated url
    s = ''

    # get the ids of the users that will be chatting
    id1 = int(request.user.id)
    id2 = int(id)

    # create the url
    if id1 < id2:
        s = str(id1)+'_'+str(id2)
    else:
        s = str(id2) + '_' + str(id1)

    # send the users to the chat url
    return redirect('../../chat/'+s)


@login_required
# this is the chat url
def chat(request, room_name):
    ids = room_name.split('_')
    if str(request.user.id) not in ids:
        return redirect('../../')
    return render(request, 'app/chat.html', {'room_name': room_name})


@login_required
# this is an ajax call to preload the last 50 messages between the two users
def get_msg(request):
    room = request.GET.get('room', None)
    all_messages = Message.objects.filter(room=room).order_by('date')[:50]
    data = {}
    fake_data = []
    for msg in all_messages:
        fake_data.append([msg.sender.username, msg.text])
    data[0] = fake_data
    return JsonResponse(data)


@login_required
# this function loads all conversations that the user has participated in
def messages(request):
    last = {}

    # get the messages that the user has sent
    messages_sent = Message.objects.filter(sender=request.user).order_by("date")

    # get the last sent message to every user
    for msg in messages_sent:
        if msg.rec in last:
            last[msg.rec].append(msg)
        else:
            last[msg.rec] = [msg]
    for key in last:
        last[key] = last[key][-1]

    # get the messages that the user has received and if he has responded check the date
    messages_rec = Message.objects.filter(rec=request.user).order_by("date")
    for msg in messages_rec:
        if msg.sender in last:
            if msg.date >= last[msg.sender].date:
                last[msg.sender] = msg
        else:
            last[msg.sender] = msg

    # sort all the messages by date
    list_of_tuples = sorted(last.items(), key=lambda x: x[1].date)[::-1]

    # search form to search for other users to chat with
    searchform = SearchForm()

    context = {'last': list_of_tuples, 'searchform': searchform}
    return render(request, 'app/messages.html', context)


@login_required
def like_post(request):
    post_id = request.GET.get('id', None)
    post = Post.objects.get(pk=post_id)

    if request.user not in post.likes.all():
        post.likes.add(request.user)
    else:
        post.likes.remove(request.user)

    post.save()
    return JsonResponse({})


@login_required
def comment_post(request):
    post_id = request.GET.get('id', None)
    post = Post.objects.get(pk=post_id)
    comment_text = request.GET.get('text', None)

    new_comment = Comment(user=request.user, post=post, text=comment_text)
    new_comment.save()

    return JsonResponse({})
