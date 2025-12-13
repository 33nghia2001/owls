"""
Reviews URLs for Owls E-commerce Platform
=========================================
"""

from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Product reviews (public)
    path('product/<uuid:product_id>/', views.ProductReviewsView.as_view(), name='product-reviews'),
    path('product/<uuid:product_id>/summary/', views.ProductReviewSummaryView.as_view(), name='product-review-summary'),
    path('product/<uuid:product_id>/can-review/', views.CanReviewView.as_view(), name='can-review'),
    
    # User's reviews
    path('my/', views.MyReviewsView.as_view(), name='my-reviews'),
    path('create/', views.CreateReviewView.as_view(), name='create-review'),
    path('<uuid:id>/', views.ReviewDetailView.as_view(), name='review-detail'),
    
    # Voting
    path('<uuid:review_id>/vote/', views.VoteReviewView.as_view(), name='vote-review'),
    path('<uuid:review_id>/vote/remove/', views.RemoveVoteView.as_view(), name='remove-vote'),
]
