from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    #homepage url (template in App/templates/App)
    path('', views.home, name='home'),
    #login and logout url (login template in App/templates/registration)
    path('accounts/', include('django.contrib.auth.urls')),
    #triggering register view
    path('register/', views.register, name='register'),
    #path to create a post
    path('addpost/', views.addpost, name='addpost'),
    #path to profile page
    path('profile/<path:user_id>/', views.profile, name='profile'),
    #delete path
    path('delete/<path:post_id>/<path:user_id>', views.delete, name='delete'),
    #path to search
    path('search/', views.searchpost, name='search'),
    path('searchprofile/', views.searchprofile, name='searchprofile'),
    path('follow/<path:id>', views.follow, name='follow'),
    path('unfollow/<path:id>', views.unfollow, name='unfollow'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)