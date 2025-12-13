"""
Banner Serializers for Owls E-commerce Platform
================================================
"""

from rest_framework import serializers
from .models import Banner, PopupBanner, SliderSettings


class BannerSerializer(serializers.ModelSerializer):
    """Serializer for banners."""

    is_currently_active = serializers.ReadOnlyField()

    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'subtitle', 'description',
            'banner_type', 'position',
            'image', 'image_mobile', 'video_url', 'html_content',
            'link_url', 'link_text', 'open_in_new_tab',
            'text_color', 'overlay_color', 'overlay_opacity',
            'start_date', 'end_date', 'order', 'is_currently_active'
        ]


class BannerListSerializer(serializers.ModelSerializer):
    """Compact serializer for banner lists."""

    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'subtitle', 'image', 'image_mobile',
            'link_url', 'link_text', 'open_in_new_tab',
            'text_color', 'overlay_color', 'overlay_opacity'
        ]


class PopupBannerSerializer(serializers.ModelSerializer):
    """Serializer for popup banners."""

    click_rate = serializers.ReadOnlyField()

    class Meta:
        model = PopupBanner
        fields = [
            'id', 'name', 'title', 'content', 'image',
            'button_text', 'button_url',
            'trigger_type', 'trigger_delay', 'trigger_scroll_percent',
            'show_once_per_session', 'show_once_per_user', 'cookie_duration_days',
            'target_pages', 'exclude_logged_in',
            'impressions', 'clicks', 'conversions', 'click_rate'
        ]


class PopupBannerPublicSerializer(serializers.ModelSerializer):
    """Public serializer for popup banners (no analytics)."""

    class Meta:
        model = PopupBanner
        fields = [
            'id', 'title', 'content', 'image',
            'button_text', 'button_url',
            'trigger_type', 'trigger_delay', 'trigger_scroll_percent',
            'show_once_per_session', 'show_once_per_user', 'cookie_duration_days'
        ]


class SliderSettingsSerializer(serializers.ModelSerializer):
    """Serializer for slider settings."""

    class Meta:
        model = SliderSettings
        fields = [
            'id', 'name',
            'autoplay', 'autoplay_speed', 'transition_speed', 'pause_on_hover',
            'show_arrows', 'show_dots', 'infinite_loop',
            'slides_to_show', 'slides_to_scroll'
        ]


class PopupImpressionSerializer(serializers.Serializer):
    """Serializer for tracking popup impressions."""
    popup_id = serializers.UUIDField()


class PopupClickSerializer(serializers.Serializer):
    """Serializer for tracking popup clicks."""
    popup_id = serializers.UUIDField()
