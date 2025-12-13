"""
Support Ticket Serializers for Owls E-commerce Platform
=======================================================
"""

from rest_framework import serializers
from .models import (
    TicketCategory, Ticket, TicketMessage,
    TicketAttachment, CannedResponse, TicketStatusHistory
)


class TicketCategorySerializer(serializers.ModelSerializer):
    """Serializer for ticket categories."""

    class Meta:
        model = TicketCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon',
            'response_time_hours', 'resolution_time_hours'
        ]


class TicketAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for ticket attachments."""

    class Meta:
        model = TicketAttachment
        fields = ['id', 'file', 'filename', 'file_size', 'mime_type', 'created_at']


class TicketMessageSerializer(serializers.ModelSerializer):
    """Serializer for ticket messages."""

    sender_display = serializers.SerializerMethodField()
    attachments = TicketAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = TicketMessage
        fields = [
            'id', 'message_type', 'sender', 'sender_name', 'sender_display',
            'content', 'is_internal', 'attachments', 'created_at'
        ]

    def get_sender_display(self, obj):
        if obj.sender:
            return obj.sender.get_full_name() or obj.sender.email
        return obj.sender_name


class CreateTicketMessageSerializer(serializers.ModelSerializer):
    """Serializer for creating ticket messages."""

    class Meta:
        model = TicketMessage
        fields = ['content', 'is_internal']


class TicketListSerializer(serializers.ModelSerializer):
    """Compact serializer for ticket list."""

    category_name = serializers.CharField(source='category.name', read_only=True)
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'subject', 'status', 'priority',
            'category', 'category_name', 'assigned_to_name',
            'created_at', 'updated_at'
        ]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.email
        return None


class TicketDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for tickets."""

    category = TicketCategorySerializer(read_only=True)
    messages = TicketMessageSerializer(many=True, read_only=True)
    attachments = TicketAttachmentSerializer(many=True, read_only=True)
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'customer_email', 'customer_name',
            'category', 'subject', 'description',
            'status', 'priority',
            'assigned_to', 'assigned_to_name', 'team',
            'order_id', 'product_id',
            'first_response_at', 'resolved_at', 'closed_at', 'sla_breached',
            'satisfaction_rating', 'satisfaction_feedback',
            'source', 'tags',
            'messages', 'attachments',
            'created_at', 'updated_at'
        ]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.email
        return None


class CreateTicketSerializer(serializers.ModelSerializer):
    """Serializer for creating tickets."""

    class Meta:
        model = Ticket
        fields = [
            'category', 'subject', 'description',
            'priority', 'order_id', 'product_id', 'source'
        ]


class UpdateTicketSerializer(serializers.ModelSerializer):
    """Serializer for updating tickets (agent)."""

    class Meta:
        model = Ticket
        fields = [
            'status', 'priority', 'assigned_to', 'team', 'tags'
        ]


class TicketStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for ticket status history."""

    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = TicketStatusHistory
        fields = [
            'id', 'old_status', 'new_status',
            'changed_by', 'changed_by_name', 'notes', 'created_at'
        ]

    def get_changed_by_name(self, obj):
        if obj.changed_by:
            return obj.changed_by.get_full_name() or obj.changed_by.email
        return 'System'


class CannedResponseSerializer(serializers.ModelSerializer):
    """Serializer for canned responses."""

    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = CannedResponse
        fields = [
            'id', 'title', 'content', 'category', 'category_name',
            'use_count', 'is_active'
        ]


class TicketSatisfactionSerializer(serializers.Serializer):
    """Serializer for ticket satisfaction rating."""

    rating = serializers.IntegerField(min_value=1, max_value=5)
    feedback = serializers.CharField(required=False, allow_blank=True)
