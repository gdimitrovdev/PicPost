# Django imports
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('addpost/', views.addpost, name='addpost'),
    path('profile/<path:user_id>/', views.profile, name='profile'),
    path('delete/<path:post_id>/<path:user_id>', views.delete, name='delete'),
    path('search/', views.searchpost, name='search'),
    path('searchprofile/', views.searchprofile, name='searchprofile'),
    path('follow/<path:id>', views.follow, name='follow'),
    path('unfollow/<path:id>', views.unfollow, name='unfollow'),
    # views.changeurl creates an url consisting of 2 users' ids (sorted)
    # the created url is the url at which the users' chat will be located
    path('changeurl/<path:id>', views.changeurl, name='changeurl'),
    # this is where the users's chat will happen using channels, websockets and ajax
    path('chat/<path:room_name>', views.chat, name='chat'),
    # this is for an ajax call that loads the messages from the model "Messages"
    # views.get_msg is called whenever an user connects to the websocket
    path('ajax/get_msg/', views.get_msg, name='get_msg'),
    path('messages/', views.messages, name='messages'),
    # path to like and dislike posts
    path('like_post', views.like_post, name='like_post')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
