"""
Banner Models for Owls E-commerce Platform
==========================================
Promotional banners, sliders, and popup management.
"""

import uuid
from django.db import models
from django.utils import timezone
from apps.base.core.users.models import TimeStampedModel


class BannerPosition(models.TextChoices):
    """Banner display positions."""
    HERO_SLIDER = 'hero_slider', 'Hero Slider'
    HOMEPAGE_TOP = 'homepage_top', 'Homepage Top'
    HOMEPAGE_MIDDLE = 'homepage_middle', 'Homepage Middle'
    HOMEPAGE_BOTTOM = 'homepage_bottom', 'Homepage Bottom'
    CATEGORY_TOP = 'category_top', 'Category Page Top'
    PRODUCT_SIDEBAR = 'product_sidebar', 'Product Sidebar'
    CART_PAGE = 'cart_page', 'Cart Page'
    CHECKOUT_PAGE = 'checkout_page', 'Checkout Page'
    POPUP = 'popup', 'Popup Modal'


class Banner(TimeStampedModel):
    """
    Promotional banner model.
    Supports images, videos, and various display positions.
    """

    class BannerType(models.TextChoices):
        IMAGE = 'image', 'Image'
        VIDEO = 'video', 'Video'
        HTML = 'html', 'HTML Content'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)

    # Display settings
    banner_type = models.CharField(
        max_length=20,
        choices=BannerType.choices,
        default=BannerType.IMAGE
    )
    position = models.CharField(
        max_length=30,
        choices=BannerPosition.choices,
        default=BannerPosition.HERO_SLIDER
    )

    # Media
    image = models.ImageField(upload_to='banners/', blank=True, null=True)
    image_mobile = models.ImageField(
        upload_to='banners/mobile/',
        blank=True, null=True,
        help_text='Mobile version of banner (optional)'
    )
    video_url = models.URLField(blank=True)
    html_content = models.TextField(blank=True, help_text='Custom HTML for HTML type banners')

    # Link settings
    link_url = models.URLField(blank=True)
    link_text = models.CharField(max_length=100, blank=True, default='Shop Now')
    open_in_new_tab = models.BooleanField(default=False)

    # Styling
    text_color = models.CharField(max_length=7, default='#FFFFFF', help_text='Hex color code')
    overlay_color = models.CharField(max_length=7, blank=True, help_text='Hex color for overlay')
    overlay_opacity = models.FloatField(default=0.3)

    # Scheduling
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    # Display order
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'banners'
        ordering = ['position', 'order', '-created_at']
        indexes = [
            models.Index(fields=['position', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_position_display()})"

    @property
    def is_currently_active(self):
        """Check if banner is active and within date range."""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


class PopupBanner(TimeStampedModel):
    """
    Popup/Modal banner model.
    Can be triggered by various conditions.
    """

    class TriggerType(models.TextChoices):
        PAGE_LOAD = 'page_load', 'On Page Load'
        EXIT_INTENT = 'exit_intent', 'On Exit Intent'
        SCROLL = 'scroll', 'On Scroll'
        TIME_DELAY = 'time_delay', 'After Time Delay'
        CART_ABANDON = 'cart_abandon', 'Cart Abandonment'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    content = models.TextField()

    # Display
    image = models.ImageField(upload_to='popups/', blank=True, null=True)
    button_text = models.CharField(max_length=50, default='Shop Now')
    button_url = models.URLField(blank=True)

    # Trigger settings
    trigger_type = models.CharField(
        max_length=20,
        choices=TriggerType.choices,
        default=TriggerType.PAGE_LOAD
    )
    trigger_delay = models.PositiveIntegerField(
        default=3,
        help_text='Seconds delay for time_delay trigger'
    )
    trigger_scroll_percent = models.PositiveIntegerField(
        default=50,
        help_text='Scroll percentage for scroll trigger'
    )

    # Frequency control
    show_once_per_session = models.BooleanField(default=True)
    show_once_per_user = models.BooleanField(default=False)
    cookie_duration_days = models.PositiveIntegerField(default=7)

    # Targeting
    target_pages = models.JSONField(
        default=list,
        help_text='List of page paths where popup should show'
    )
    exclude_logged_in = models.BooleanField(default=False)

    # Scheduling
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Analytics
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    conversions = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'popup_banners'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def click_rate(self):
        if self.impressions == 0:
            return 0
        return round((self.clicks / self.impressions) * 100, 2)


class SliderSettings(TimeStampedModel):
    """
    Global slider settings model.
    Configures behavior of hero slider.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, default='default')

    # Animation settings
    autoplay = models.BooleanField(default=True)
    autoplay_speed = models.PositiveIntegerField(default=5000, help_text='Milliseconds')
    transition_speed = models.PositiveIntegerField(default=500, help_text='Milliseconds')
    pause_on_hover = models.BooleanField(default=True)

    # Navigation
    show_arrows = models.BooleanField(default=True)
    show_dots = models.BooleanField(default=True)
    infinite_loop = models.BooleanField(default=True)

    # Display
    slides_to_show = models.PositiveIntegerField(default=1)
    slides_to_scroll = models.PositiveIntegerField(default=1)

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'slider_settings'
        verbose_name_plural = 'Slider Settings'

    def __str__(self):
        return f"Slider Settings: {self.name}"
