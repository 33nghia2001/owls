"""
Support Ticket URLs for Owls E-commerce Platform
================================================
"""

from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    # Public/Customer endpoints
    path('categories/', views.TicketCategoryListView.as_view(), name='categories'),

    # Customer ticket management
    path('tickets/', views.MyTicketsView.as_view(), name='my-tickets'),
    path('tickets/<str:ticket_number>/', views.MyTicketDetailView.as_view(), name='ticket-detail'),
    path('tickets/<str:ticket_number>/message/', views.AddTicketMessageView.as_view(), name='add-message'),
    path('tickets/<str:ticket_number>/rate/', views.RateTicketView.as_view(), name='rate-ticket'),

    # Agent/Admin endpoints
    path('admin/tickets/', views.AllTicketsView.as_view(), name='all-tickets'),
    path('admin/tickets/<str:ticket_number>/', views.AdminTicketDetailView.as_view(), name='admin-ticket-detail'),
    path('admin/tickets/<str:ticket_number>/reply/', views.AgentReplyView.as_view(), name='agent-reply'),
    path('admin/tickets/<str:ticket_number>/assign/', views.AssignTicketView.as_view(), name='assign-ticket'),
    path('admin/tickets/<str:ticket_number>/history/', views.TicketStatusHistoryView.as_view(), name='status-history'),

    # Agent tools
    path('admin/canned-responses/', views.CannedResponseListView.as_view(), name='canned-responses'),
    path('admin/stats/', views.TicketStatsView.as_view(), name='stats'),
]
