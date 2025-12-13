"""
Fraud Detection Serializers for Owls E-commerce Platform
========================================================
"""

from rest_framework import serializers
from .models import (
    FraudRule, RiskAssessment, TriggeredRule,
    IPBlacklist, DeviceFingerprint
)


class FraudRuleSerializer(serializers.ModelSerializer):
    """Serializer for FraudRule model."""
    
    class Meta:
        model = FraudRule
        fields = [
            'id', 'name', 'description', 'rule_type', 'conditions',
            'action', 'risk_score', 'priority', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TriggeredRuleSerializer(serializers.ModelSerializer):
    """Serializer for TriggeredRule."""
    
    rule_name = serializers.CharField(source='rule.name', read_only=True)
    rule_type = serializers.CharField(source='rule.rule_type', read_only=True)
    rule_action = serializers.CharField(source='rule.action', read_only=True)
    
    class Meta:
        model = TriggeredRule
        fields = [
            'id', 'rule', 'rule_name', 'rule_type', 'rule_action',
            'matched_value', 'details', 'created_at'
        ]


class RiskAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for RiskAssessment model."""
    
    rule_triggers = TriggeredRuleSerializer(many=True, read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    reviewed_by_name = serializers.CharField(
        source='reviewed_by.full_name',
        read_only=True,
        default=''
    )
    
    class Meta:
        model = RiskAssessment
        fields = [
            'id', 'order', 'order_number', 'user', 'user_email',
            'risk_score', 'risk_level', 'status',
            'ip_address', 'user_agent', 'device_fingerprint',
            'country_code', 'city', 'order_amount', 'payment_method',
            'analysis_data', 'rule_triggers',
            'reviewed_by', 'reviewed_by_name', 'reviewed_at', 'review_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order', 'user', 'risk_score', 'risk_level',
            'analysis_data', 'created_at', 'updated_at'
        ]


class RiskAssessmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    triggered_rules_count = serializers.IntegerField(
        source='rule_triggers.count',
        read_only=True
    )
    
    class Meta:
        model = RiskAssessment
        fields = [
            'id', 'order_number', 'user_email', 'risk_score', 'risk_level',
            'status', 'order_amount', 'triggered_rules_count', 'created_at'
        ]


class ReviewAssessmentSerializer(serializers.Serializer):
    """Serializer for reviewing an assessment."""
    
    status = serializers.ChoiceField(choices=[
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('escalated', 'Escalated')
    ])
    review_notes = serializers.CharField(required=False, allow_blank=True)


class IPBlacklistSerializer(serializers.ModelSerializer):
    """Serializer for IPBlacklist model."""
    
    is_active = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(
        source='created_by.full_name',
        read_only=True,
        default=''
    )
    
    class Meta:
        model = IPBlacklist
        fields = [
            'id', 'ip_address', 'reason', 'notes', 'expires_at',
            'is_active', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class BlockIPSerializer(serializers.Serializer):
    """Serializer for blocking an IP."""
    
    ip_address = serializers.IPAddressField()
    reason = serializers.ChoiceField(choices=IPBlacklist.Reason.choices)
    notes = serializers.CharField(required=False, allow_blank=True)
    expires_hours = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=8760,  # 1 year max
        help_text='Hours until expiry (leave empty for permanent)'
    )


class DeviceFingerprintSerializer(serializers.ModelSerializer):
    """Serializer for DeviceFingerprint model."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = DeviceFingerprint
        fields = [
            'id', 'fingerprint', 'user', 'user_email',
            'device_type', 'os', 'browser',
            'is_trusted', 'is_blocked', 'block_reason',
            'first_seen', 'last_seen', 'login_count', 'order_count'
        ]
        read_only_fields = [
            'id', 'fingerprint', 'user', 'first_seen', 'last_seen',
            'login_count', 'order_count'
        ]


class FraudStatsSerializer(serializers.Serializer):
    """Serializer for fraud statistics."""
    
    total_assessments = serializers.IntegerField()
    pending_review = serializers.IntegerField()
    approved = serializers.IntegerField()
    rejected = serializers.IntegerField()
    
    by_risk_level = serializers.DictField()
    recent_high_risk = serializers.IntegerField()
    blocked_ips = serializers.IntegerField()
    blocked_devices = serializers.IntegerField()
