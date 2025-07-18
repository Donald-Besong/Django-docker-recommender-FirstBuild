from django.urls import path, include
from donald_project import settings

from . views import (
    PostListView,
    PostDetailView,
    PostCreateView, PostUpdateView,
    PostDeleteView,
    UserPostListView,
    )
from . import views

if settings.USE_S3:
    movies_path = path('post/movies/', views.movies_s3_view, name='post-movies')
else:
    movies_path = path('post/movies/', views.movies_view, name='post-movies')


urlpatterns = [
    # path('', views.home_view, name='home'),
    # path('home/', views.home_view, name='home'),
    path('health/', views.health, name='health'),
    path('post/result', views.movies_result_view, name='movies_result'),
    path('', PostListView.as_view(), name='home'),
    path('home/', PostListView.as_view(), name='home'),
    path('about/', views.about_view, name='about'),
    path('prepare/', views.movies_prepare, name='prepare'),
    path('movieserror/', views.movieserror_view, name='movieserror'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    movies_path,
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('user/<str:username>/', UserPostListView.as_view(), name='user-posts'),
]
