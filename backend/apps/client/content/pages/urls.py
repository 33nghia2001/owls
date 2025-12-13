"""
Pages URLs for Owls E-commerce Platform
=======================================
"""

from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    # Navigation pages
    path('menu/', views.MenuPagesView.as_view(), name='menu-pages'),
    path('footer/', views.FooterPagesView.as_view(), name='footer-pages'),

    # Special pages
    path('about/', views.AboutPageView.as_view(), name='about'),
    path('privacy/', views.PrivacyPolicyView.as_view(), name='privacy'),
    path('terms/', views.TermsOfServiceView.as_view(), name='terms'),

    # Contact form
    path('contact/', views.ContactFormView.as_view(), name='contact'),

    # FAQs
    path('faqs/', views.FAQListView.as_view(), name='faq-list'),
    path('faqs/search/', views.FAQSearchView.as_view(), name='faq-search'),
    path('faqs/<uuid:pk>/helpful/', views.FAQHelpfulView.as_view(), name='faq-helpful'),

    # Dynamic pages by slug (must be last)
    path('<slug:slug>/', views.PageDetailView.as_view(), name='page-detail'),
]
