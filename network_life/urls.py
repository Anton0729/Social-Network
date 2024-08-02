from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'network_life'

urlpatterns = [
    path('', views.home, name='home'),
    path('liked/<int:post_id>', views.like_unlike_post, name='like-post-view'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('login_via_accounts/', views.login_via_accounts, name='login_via_accounts'),
    path('logout/', views.logout_user, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path("create/", views.create_post, name='create'),
    path("post/<int:id>", views.post, name='post'),
    path("profile/<str:username>", views.profile, name='profile'),
    path("update_profile", views.update_profile, name='update_profile'),
    path("follow/<str:follower>/<str:user>", views.follow, name='follow'),
    path('following_accounts/<str:username>', views.following_accounts, name='following_accounts'),
    path('followers_accounts/<str:username>', views.followers_accounts, name='followers_accounts'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
