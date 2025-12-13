"""
Fraud Detection Models for Owls E-commerce Platform
====================================================
Risk assessment and fraud prevention system.
"""

import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MaxValueValidator


class FraudRule(models.Model):
    """
    Configurable fraud detection rules.
    
    Rules are evaluated in priority order, and actions are taken based on
    the highest severity match.
    """
    
    class RuleType(models.TextChoices):
        VELOCITY = 'velocity', 'Velocity Check'
        AMOUNT = 'amount', 'Amount Threshold'
        IP_CHECK = 'ip', 'IP Address Check'
        DEVICE = 'device', 'Device Fingerprint'
        LOCATION = 'location', 'Geolocation Check'
        BEHAVIOR = 'behavior', 'Behavioral Analysis'
        BLACKLIST = 'blacklist', 'Blacklist Check'
        CUSTOM = 'custom', 'Custom Rule'
    
    class Action(models.TextChoices):
        ALLOW = 'allow', 'Allow'
        FLAG = 'flag', 'Flag for Review'
        BLOCK = 'block', 'Block'
        CHALLENGE = 'challenge', 'Require Verification'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    rule_type = models.CharField(
        max_length=20,
        choices=RuleType.choices,
        db_index=True
    )
    
    # Rule configuration (JSON for flexibility)
    conditions = models.JSONField(
        default=dict,
        help_text='Rule conditions in JSON format'
    )
    
    # Action to take when rule matches
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
        default=Action.FLAG
    )
    
    # Risk score contribution (0-100)
    risk_score = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        help_text='Risk score added when rule matches (0-100)'
    )
    
    # Priority (lower = higher priority)
    priority = models.PositiveIntegerField(
        default=100,
        help_text='Rule evaluation priority (lower = evaluated first)'
    )
    
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fraud_rules'
        ordering = ['priority', 'name']
        indexes = [
            models.Index(fields=['rule_type', 'is_active']),
        ]
    
    def __str__(self):
        return f'{self.name} ({self.rule_type})'


class RiskAssessment(models.Model):
    """
    Risk assessment record for orders/transactions.
    
    Stores the result of fraud detection analysis.
    """
    
    class RiskLevel(models.TextChoices):
        LOW = 'low', 'Low Risk'
        MEDIUM = 'medium', 'Medium Risk'
        HIGH = 'high', 'High Risk'
        CRITICAL = 'critical', 'Critical Risk'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Review'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        ESCALATED = 'escalated', 'Escalated'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # What's being assessed
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='risk_assessment',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='risk_assessments'
    )
    
    # Risk scores
    risk_score = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        help_text='Overall risk score (0-100)'
    )
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
        db_index=True
    )
    
    # Assessment status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    
    # Triggered rules
    triggered_rules = models.ManyToManyField(
        FraudRule,
        through='TriggeredRule',
        related_name='assessments'
    )
    
    # Context data for assessment
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    device_fingerprint = models.CharField(max_length=255, blank=True)
    
    # Location data
    country_code = models.CharField(max_length=2, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Order data snapshot
    order_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    payment_method = models.CharField(max_length=50, blank=True)
    
    # Analysis details
    analysis_data = models.JSONField(
        default=dict,
        help_text='Detailed analysis results'
    )
    
    # Review
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_assessments'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'risk_assessments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['risk_level', 'status']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f'Assessment {self.id} - {self.risk_level}'
    
    @classmethod
    def calculate_risk_level(cls, score: int) -> str:
        """Calculate risk level from score."""
        if score >= 80:
            return cls.RiskLevel.CRITICAL
        elif score >= 60:
            return cls.RiskLevel.HIGH
        elif score >= 30:
            return cls.RiskLevel.MEDIUM
        return cls.RiskLevel.LOW


class TriggeredRule(models.Model):
    """
    Junction table for assessment and triggered rules.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(
        RiskAssessment,
        on_delete=models.CASCADE,
        related_name='rule_triggers'
    )
    rule = models.ForeignKey(
        FraudRule,
        on_delete=models.CASCADE,
        related_name='triggers'
    )
    
    # What triggered this rule
    matched_value = models.CharField(
        max_length=255,
        blank=True,
        help_text='The value that triggered this rule'
    )
    details = models.JSONField(
        default=dict,
        help_text='Additional details about the match'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'triggered_rules'
        unique_together = ['assessment', 'rule']


class IPBlacklist(models.Model):
    """
    Blacklisted IP addresses.
    """
    
    class Reason(models.TextChoices):
        FRAUD = 'fraud', 'Fraud Attempt'
        ABUSE = 'abuse', 'Abuse/Spam'
        BOT = 'bot', 'Bot Activity'
        VPN = 'vpn', 'VPN/Proxy'
        TOR = 'tor', 'Tor Exit Node'
        MANUAL = 'manual', 'Manual Block'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    ip_address = models.GenericIPAddressField(unique=True, db_index=True)
    reason = models.CharField(
        max_length=20,
        choices=Reason.choices,
        default=Reason.MANUAL
    )
    notes = models.TextField(blank=True)
    
    # Can be temporary
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Leave empty for permanent block'
    )
    
    # Who blocked
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ip_blacklist'
        verbose_name_plural = 'IP Blacklist'
    
    def __str__(self):
        return f'{self.ip_address} ({self.reason})'
    
    @property
    def is_active(self):
        """Check if blacklist entry is still active."""
        if self.expires_at is None:
            return True
        return self.expires_at > timezone.now()


class DeviceFingerprint(models.Model):
    """
    Track device fingerprints for fraud detection.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    fingerprint = models.CharField(max_length=255, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='device_fingerprints'
    )
    
    # Device info
    device_type = models.CharField(max_length=50, blank=True)  # mobile, desktop, tablet
    os = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=50, blank=True)
    
    # Trust status
    is_trusted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False, db_index=True)
    block_reason = models.CharField(max_length=255, blank=True)
    
    # Stats
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    login_count = models.PositiveIntegerField(default=0)
    order_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'device_fingerprints'
    
    def __str__(self):
        return f'{self.fingerprint[:20]}... ({self.device_type})'


class VelocityCounter(models.Model):
    """
    Track velocity metrics for fraud detection.
    
    Used to count events (orders, logins, etc.) within time windows.
    """
    
    class CounterType(models.TextChoices):
        ORDER_BY_USER = 'order_user', 'Orders by User'
        ORDER_BY_IP = 'order_ip', 'Orders by IP'
        ORDER_BY_CARD = 'order_card', 'Orders by Card'
        LOGIN_BY_USER = 'login_user', 'Logins by User'
        LOGIN_BY_IP = 'login_ip', 'Logins by IP'
        FAILED_PAYMENT = 'failed_payment', 'Failed Payments'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    counter_type = models.CharField(
        max_length=30,
        choices=CounterType.choices,
        db_index=True
    )
    identifier = models.CharField(
        max_length=255,
        db_index=True,
        help_text='User ID, IP address, or card hash'
    )
    
    # Time window
    window_start = models.DateTimeField()
    window_end = models.DateTimeField()
    
    # Counter
    count = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Total amount for this window (for orders)'
    )
    
    class Meta:
        db_table = 'velocity_counters'
        unique_together = ['counter_type', 'identifier', 'window_start']
        indexes = [
            models.Index(fields=['counter_type', 'identifier', 'window_end']),
        ]
    
    def __str__(self):
        return f'{self.counter_type}: {self.identifier} = {self.count}'
