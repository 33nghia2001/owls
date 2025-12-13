"""
Blog URLs for Owls E-commerce Platform
======================================
"""

from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Categories and Tags
    path('categories/', views.BlogCategoryListView.as_view(), name='category-list'),
    path('tags/', views.BlogTagListView.as_view(), name='tag-list'),

    # Post listings
    path('posts/', views.BlogPostListView.as_view(), name='post-list'),
    path('posts/featured/', views.FeaturedPostsView.as_view(), name='featured-posts'),
    path('posts/recent/', views.RecentPostsView.as_view(), name='recent-posts'),
    path('posts/popular/', views.PopularPostsView.as_view(), name='popular-posts'),
    path('posts/search/', views.SearchBlogView.as_view(), name='search'),

    # Single post
    path('posts/<slug:slug>/', views.BlogPostDetailView.as_view(), name='post-detail'),
    path('posts/<slug:slug>/related/', views.RelatedPostsView.as_view(), name='related-posts'),
    path('posts/<slug:slug>/comments/', views.BlogPostCommentsView.as_view(), name='post-comments'),
]
