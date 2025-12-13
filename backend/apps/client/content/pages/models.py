"""
Pages Models for Owls E-commerce Platform
=========================================
Static pages and CMS content.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from apps.base.core.system.models import TimeStampedModel


class Page(TimeStampedModel):
    """
    Static page model for CMS content.
    Examples: About Us, Contact, Privacy Policy, Terms of Service
    """
    
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PUBLISHED = 'published', _('Published')
        ARCHIVED = 'archived', _('Archived')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Basic info
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=280, unique=True)
    
    # Content
    content = models.TextField(_('Content'))
    excerpt = models.TextField(_('Excerpt'), max_length=500, blank=True)
    
    # Media
    featured_image = models.ImageField(
        _('Featured image'),
        upload_to='pages/',
        blank=True,
        null=True
    )
    
    # Hierarchy
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='children',
        blank=True,
        null=True
    )
    
    # Status
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    # SEO
    meta_title = models.CharField(_('Meta title'), max_length=70, blank=True)
    meta_description = models.TextField(_('Meta description'), max_length=160, blank=True)
    
    # Display settings
    show_in_menu = models.BooleanField(_('Show in menu'), default=False)
    show_in_footer = models.BooleanField(_('Show in footer'), default=False)
    menu_order = models.PositiveIntegerField(_('Menu order'), default=0)
    
    # Template
    template = models.CharField(
        _('Template'),
        max_length=100,
        default='default',
        help_text=_('Template name for custom page layouts')
    )

    class Meta:
        app_label = 'pages'
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')
        ordering = ['menu_order', 'title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class FAQ(TimeStampedModel):
    """Frequently Asked Questions."""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    category = models.CharField(
        _('Category'),
        max_length=50,
        choices=[
            ('general', _('General')),
            ('orders', _('Orders')),
            ('shipping', _('Shipping')),
            ('returns', _('Returns & Refunds')),
            ('payment', _('Payment')),
            ('account', _('Account')),
        ],
        default='general'
    )
    
    question = models.CharField(_('Question'), max_length=500)
    answer = models.TextField(_('Answer'))
    
    order = models.PositiveIntegerField(_('Order'), default=0)
    is_active = models.BooleanField(_('Active'), default=True)
    is_featured = models.BooleanField(_('Featured'), default=False)
    
    # Stats
    helpful_count = models.PositiveIntegerField(_('Helpful votes'), default=0)
    not_helpful_count = models.PositiveIntegerField(_('Not helpful votes'), default=0)

    class Meta:
        app_label = 'pages'
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        ordering = ['category', 'order']

    def __str__(self):
        return self.question


class ContactMessage(TimeStampedModel):
    """Contact form submissions."""
    
    class Status(models.TextChoices):
        NEW = 'new', _('New')
        IN_PROGRESS = 'in_progress', _('In Progress')
        RESOLVED = 'resolved', _('Resolved')
        SPAM = 'spam', _('Spam')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Sender info
    name = models.CharField(_('Name'), max_length=100)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Phone'), max_length=20, blank=True)
    
    # Message
    subject = models.CharField(_('Subject'), max_length=255)
    message = models.TextField(_('Message'))
    
    # User (if logged in)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='contact_messages',
        blank=True,
        null=True
    )
    
    # Status
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )
    
    # Response
    response = models.TextField(_('Response'), blank=True)
    responded_at = models.DateTimeField(_('Responded at'), blank=True, null=True)
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='contact_responses',
        blank=True,
        null=True
    )

    class Meta:
        app_label = 'pages'
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.email}"
