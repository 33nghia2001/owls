"""
Support Ticket Models for Owls E-commerce Platform
==================================================
Customer support ticket system.
"""

import uuid
from django.db import models
from django.conf import settings
from apps.base.core.users.models import TimeStampedModel


class TicketCategory(TimeStampedModel):
    """
    Categories for support tickets.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    # SLA settings
    response_time_hours = models.PositiveIntegerField(
        default=24,
        help_text='Target first response time in hours'
    )
    resolution_time_hours = models.PositiveIntegerField(
        default=72,
        help_text='Target resolution time in hours'
    )

    # Auto-assignment
    default_assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='default_ticket_categories'
    )

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'ticket_categories'
        verbose_name_plural = 'Ticket Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Ticket(TimeStampedModel):
    """
    Support ticket model.
    """

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        WAITING_CUSTOMER = 'waiting_customer', 'Waiting on Customer'
        WAITING_INTERNAL = 'waiting_internal', 'Waiting on Internal'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=20, unique=True)

    # Customer
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_tickets'
    )
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=200)

    # Ticket details
    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='tickets'
    )
    subject = models.CharField(max_length=300)
    description = models.TextField()

    # Status and priority
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_tickets'
    )
    team = models.CharField(max_length=100, blank=True)

    # Related entities
    order_id = models.UUIDField(null=True, blank=True)
    product_id = models.UUIDField(null=True, blank=True)

    # SLA tracking
    first_response_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    sla_breached = models.BooleanField(default=False)

    # Customer satisfaction
    satisfaction_rating = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='1-5 rating'
    )
    satisfaction_feedback = models.TextField(blank=True)

    # Metadata
    source = models.CharField(
        max_length=30,
        default='web',
        choices=[
            ('web', 'Website'),
            ('mobile', 'Mobile App'),
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('chat', 'Live Chat'),
            ('social', 'Social Media'),
        ]
    )
    tags = models.JSONField(default=list)

    class Meta:
        db_table = 'tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['ticket_number']),
        ]

    def __str__(self):
        return f"#{self.ticket_number}: {self.subject}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            # Generate ticket number
            import random
            self.ticket_number = f"TKT{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)


class TicketMessage(TimeStampedModel):
    """
    Messages within a ticket thread.
    """

    class MessageType(models.TextChoices):
        CUSTOMER = 'customer', 'Customer Message'
        AGENT = 'agent', 'Agent Reply'
        SYSTEM = 'system', 'System Message'
        NOTE = 'note', 'Internal Note'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    message_type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
        default=MessageType.CUSTOMER
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ticket_messages'
    )
    sender_name = models.CharField(max_length=200)
    content = models.TextField()

    # For internal notes
    is_internal = models.BooleanField(default=False)

    class Meta:
        db_table = 'ticket_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"Message on {self.ticket.ticket_number}"


class TicketAttachment(TimeStampedModel):
    """
    File attachments for tickets.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    message = models.ForeignKey(
        TicketMessage,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='attachments'
    )

    file = models.FileField(upload_to='tickets/attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ticket_uploads'
    )

    class Meta:
        db_table = 'ticket_attachments'
        ordering = ['-created_at']

    def __str__(self):
        return self.filename


class CannedResponse(TimeStampedModel):
    """
    Pre-written responses for common issues.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='canned_responses'
    )

    # Usage tracking
    use_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_canned_responses'
    )

    class Meta:
        db_table = 'canned_responses'
        ordering = ['-use_count', 'title']

    def __str__(self):
        return self.title


class TicketStatusHistory(TimeStampedModel):
    """
    Track ticket status changes.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='status_history'
    )

    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ticket_status_changes'
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'ticket_status_history'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticket.ticket_number}: {self.old_status} -> {self.new_status}"
