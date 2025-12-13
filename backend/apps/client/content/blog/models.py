"""
Blog Models for Owls E-commerce Platform
========================================
Blog posts and content management.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify
from apps.base.core.system.models import TimeStampedModel


class BlogCategory(TimeStampedModel):
    """Blog post categories."""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), max_length=120, unique=True)
    description = models.TextField(_('Description'), blank=True)
    image = models.ImageField(
        _('Image'),
        upload_to='blog/categories/',
        blank=True,
        null=True
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='children',
        blank=True,
        null=True
    )
    
    order = models.PositiveIntegerField(_('Order'), default=0)
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        app_label = 'blog'
        verbose_name = _('Blog Category')
        verbose_name_plural = _('Blog Categories')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogTag(TimeStampedModel):
    """Blog post tags."""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(_('Name'), max_length=50, unique=True)
    slug = models.SlugField(_('Slug'), max_length=60, unique=True)

    class Meta:
        app_label = 'blog'
        verbose_name = _('Blog Tag')
        verbose_name_plural = _('Blog Tags')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(TimeStampedModel):
    """Blog post model."""
    
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PUBLISHED = 'published', _('Published')
        SCHEDULED = 'scheduled', _('Scheduled')
        ARCHIVED = 'archived', _('Archived')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Author
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='blog_posts',
        blank=True,
        null=True
    )
    
    # Content
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=280, unique=True)
    excerpt = models.TextField(_('Excerpt'), max_length=500, blank=True)
    content = models.TextField(_('Content'))
    
    # Media
    featured_image = models.ImageField(
        _('Featured image'),
        upload_to='blog/posts/%Y/%m/',
        blank=True,
        null=True
    )
    featured_video = models.URLField(_('Featured video URL'), blank=True)
    
    # Categorization
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True
    )
    tags = models.ManyToManyField(
        BlogTag,
        related_name='posts',
        blank=True
    )
    
    # Status & Publishing
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True
    )
    published_at = models.DateTimeField(
        _('Published at'),
        blank=True,
        null=True
    )
    
    # SEO
    meta_title = models.CharField(_('Meta title'), max_length=70, blank=True)
    meta_description = models.TextField(_('Meta description'), max_length=160, blank=True)
    meta_keywords = models.CharField(_('Meta keywords'), max_length=255, blank=True)
    
    # Stats
    view_count = models.PositiveIntegerField(_('View count'), default=0)
    
    # Features
    is_featured = models.BooleanField(_('Featured'), default=False)
    allow_comments = models.BooleanField(_('Allow comments'), default=True)
    
    # Reading time (auto-calculated)
    reading_time = models.PositiveIntegerField(
        _('Reading time (minutes)'),
        default=1
    )

    class Meta:
        app_label = 'blog'
        verbose_name = _('Blog Post')
        verbose_name_plural = _('Blog Posts')
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Calculate reading time (avg 200 words per minute)
        word_count = len(self.content.split())
        self.reading_time = max(1, word_count // 200)
        
        # Auto-publish
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)

    def increment_views(self):
        """Increment view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class BlogComment(TimeStampedModel):
    """Blog post comments."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        APPROVED = 'approved', _('Approved')
        SPAM = 'spam', _('Spam')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='blog_comments',
        blank=True,
        null=True
    )
    
    # For anonymous comments
    name = models.CharField(_('Name'), max_length=100, blank=True)
    email = models.EmailField(_('Email'), blank=True)
    
    content = models.TextField(_('Content'), max_length=2000)
    
    # Reply
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        blank=True,
        null=True
    )
    
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    class Meta:
        app_label = 'blog'
        verbose_name = _('Blog Comment')
        verbose_name_plural = _('Blog Comments')
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment on {self.post.title}"
