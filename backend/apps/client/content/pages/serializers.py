"""
Pages Serializers for Owls E-commerce Platform
==============================================
"""

from rest_framework import serializers
from .models import Page, FAQ, ContactMessage


class PageListSerializer(serializers.ModelSerializer):
    """Compact serializer for page list."""

    class Meta:
        model = Page
        fields = ['id', 'title', 'slug', 'page_type', 'show_in_menu', 'menu_order']


class PageDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for page content."""

    class Meta:
        model = Page
        fields = [
            'id', 'title', 'slug', 'page_type', 'content',
            'featured_image', 'meta_title', 'meta_description',
            'updated_at'
        ]


class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQ items."""

    class Meta:
        model = FAQ
        fields = [
            'id', 'question', 'answer', 'category',
            'helpful_count', 'order'
        ]


class FAQCategorySerializer(serializers.Serializer):
    """Serializer for FAQ categories grouped."""
    
    category = serializers.CharField()
    faqs = FAQSerializer(many=True)


class ContactMessageSerializer(serializers.ModelSerializer):
    """Serializer for creating contact messages."""

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']

    def create(self, validated_data):
        return ContactMessage.objects.create(**validated_data)


class ContactMessageDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for contact messages (admin)."""

    class Meta:
        model = ContactMessage
        fields = '__all__'
