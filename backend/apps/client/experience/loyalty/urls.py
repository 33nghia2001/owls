"""
Loyalty URLs for Owls E-commerce Platform
=========================================
"""

from django.urls import path
from . import views

app_name = 'loyalty'

urlpatterns = [
    # Tiers
    path('tiers/', views.LoyaltyTiersView.as_view(), name='loyalty-tiers'),
    
    # Account
    path('account/', views.MyLoyaltyAccountView.as_view(), name='my-loyalty-account'),
    path('summary/', views.MyLoyaltySummaryView.as_view(), name='my-loyalty-summary'),
    path('transactions/', views.MyPointTransactionsView.as_view(), name='my-transactions'),
    
    # Rewards
    path('rewards/', views.AvailableRewardsView.as_view(), name='available-rewards'),
    path('rewards/featured/', views.FeaturedRewardsView.as_view(), name='featured-rewards'),
    path('rewards/redeem/', views.RedeemRewardView.as_view(), name='redeem-reward'),
    
    # Redemptions
    path('redemptions/', views.MyRedemptionsView.as_view(), name='my-redemptions'),
    path('redemptions/<uuid:id>/', views.RedemptionDetailView.as_view(), name='redemption-detail'),
]
