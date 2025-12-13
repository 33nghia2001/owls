"""
Fraud Detection Services for Owls E-commerce Platform
======================================================
Core fraud detection and risk assessment logic.
"""

import logging
from decimal import Decimal
from typing import Optional, Tuple
from datetime import timedelta
from django.db import transaction
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache

from .models import (
    FraudRule, RiskAssessment, TriggeredRule,
    IPBlacklist, DeviceFingerprint, VelocityCounter
)

logger = logging.getLogger(__name__)


class FraudDetectionService:
    """
    Main fraud detection service.
    
    Analyzes orders and transactions for potential fraud based on
    configurable rules and behavioral patterns.
    """
    
    # Risk thresholds
    RISK_THRESHOLD_BLOCK = 80
    RISK_THRESHOLD_FLAG = 50
    
    # Velocity limits (defaults, can be overridden by rules)
    DEFAULT_VELOCITY_LIMITS = {
        'orders_per_hour_user': 5,
        'orders_per_hour_ip': 10,
        'orders_per_day_user': 20,
        'amount_per_hour_user': Decimal('50000000'),  # 50M VND
        'amount_per_day_user': Decimal('200000000'),  # 200M VND
        'failed_payments_per_hour': 5,
    }
    
    def __init__(self):
        self.rules = self._load_active_rules()
    
    def _load_active_rules(self) -> list:
        """Load and cache active fraud rules."""
        cache_key = 'fraud_rules_active'
        rules = cache.get(cache_key)
        
        if rules is None:
            rules = list(
                FraudRule.objects.filter(is_active=True)
                .order_by('priority')
            )
            cache.set(cache_key, rules, 300)  # 5 minutes cache
        
        return rules
    
    def assess_order(
        self,
        order,
        ip_address: str = None,
        user_agent: str = None,
        device_fingerprint: str = None
    ) -> RiskAssessment:
        """
        Perform full fraud assessment on an order.
        
        Returns RiskAssessment with risk score and triggered rules.
        """
        user = order.user
        
        # Create assessment record
        assessment = RiskAssessment.objects.create(
            order=order,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent or '',
            device_fingerprint=device_fingerprint or '',
            order_amount=order.total,
            payment_method=order.payment_method if hasattr(order, 'payment_method') else ''
        )
        
        total_score = 0
        triggered = []
        analysis_data = {}
        
        # 1. Check IP blacklist
        if ip_address:
            ip_result = self._check_ip_blacklist(ip_address)
            if ip_result['blocked']:
                total_score += 100
                triggered.append(('IP Blacklist', ip_result))
                analysis_data['ip_check'] = ip_result
        
        # 2. Check device fingerprint
        if device_fingerprint:
            device_result = self._check_device(device_fingerprint, user)
            if device_result['risk_score'] > 0:
                total_score += device_result['risk_score']
                triggered.append(('Device Check', device_result))
            analysis_data['device_check'] = device_result
        
        # 3. Velocity checks
        velocity_result = self._check_velocity(user, ip_address, order.total)
        if velocity_result['risk_score'] > 0:
            total_score += velocity_result['risk_score']
            triggered.append(('Velocity Check', velocity_result))
        analysis_data['velocity_check'] = velocity_result
        
        # 4. Amount checks
        amount_result = self._check_amount(user, order.total)
        if amount_result['risk_score'] > 0:
            total_score += amount_result['risk_score']
            triggered.append(('Amount Check', amount_result))
        analysis_data['amount_check'] = amount_result
        
        # 5. User behavior checks
        behavior_result = self._check_user_behavior(user)
        if behavior_result['risk_score'] > 0:
            total_score += behavior_result['risk_score']
            triggered.append(('Behavior Check', behavior_result))
        analysis_data['behavior_check'] = behavior_result
        
        # 6. Apply custom rules
        for rule in self.rules:
            rule_result = self._evaluate_rule(rule, order, user, analysis_data)
            if rule_result['matched']:
                total_score += rule.risk_score
                triggered.append((rule.name, rule_result))
                
                # Create triggered rule record
                TriggeredRule.objects.create(
                    assessment=assessment,
                    rule=rule,
                    matched_value=rule_result.get('matched_value', ''),
                    details=rule_result
                )
        
        # Cap score at 100
        total_score = min(total_score, 100)
        
        # Determine risk level and status
        risk_level = RiskAssessment.calculate_risk_level(total_score)
        
        if total_score >= self.RISK_THRESHOLD_BLOCK:
            status = RiskAssessment.Status.REJECTED
        elif total_score >= self.RISK_THRESHOLD_FLAG:
            status = RiskAssessment.Status.PENDING
        else:
            status = RiskAssessment.Status.APPROVED
        
        # Update assessment
        assessment.risk_score = total_score
        assessment.risk_level = risk_level
        assessment.status = status
        assessment.analysis_data = analysis_data
        assessment.save()
        
        logger.info(
            f"Risk assessment for order {order.order_number}: "
            f"score={total_score}, level={risk_level}, status={status}"
        )
        
        return assessment
    
    def _check_ip_blacklist(self, ip_address: str) -> dict:
        """Check if IP is blacklisted."""
        try:
            blacklist = IPBlacklist.objects.get(ip_address=ip_address)
            if blacklist.is_active:
                return {
                    'blocked': True,
                    'reason': blacklist.reason,
                    'risk_score': 100
                }
        except IPBlacklist.DoesNotExist:
            pass
        
        return {'blocked': False, 'risk_score': 0}
    
    def _check_device(self, fingerprint: str, user) -> dict:
        """Check device fingerprint."""
        result = {'risk_score': 0, 'issues': []}
        
        device, created = DeviceFingerprint.objects.get_or_create(
            fingerprint=fingerprint,
            defaults={'user': user}
        )
        
        if device.is_blocked:
            result['risk_score'] = 80
            result['issues'].append(f'Device blocked: {device.block_reason}')
            return result
        
        # New device for existing user
        if created and user.orders.count() > 0:
            result['risk_score'] += 10
            result['issues'].append('New device for existing user')
        
        # Device used by multiple users
        if not created and device.user and device.user != user:
            result['risk_score'] += 30
            result['issues'].append('Device associated with different user')
        
        # Update device stats
        device.last_seen = timezone.now()
        device.order_count += 1
        if device.user is None:
            device.user = user
        device.save(update_fields=['last_seen', 'order_count', 'user'])
        
        return result
    
    def _check_velocity(
        self,
        user,
        ip_address: str,
        amount: Decimal
    ) -> dict:
        """Check velocity limits."""
        result = {'risk_score': 0, 'issues': []}
        now = timezone.now()
        
        # Orders per hour by user
        hour_ago = now - timedelta(hours=1)
        user_orders_hour = user.orders.filter(created_at__gte=hour_ago).count()
        limit = self.DEFAULT_VELOCITY_LIMITS['orders_per_hour_user']
        if user_orders_hour >= limit:
            result['risk_score'] += 30
            result['issues'].append(f'User exceeded {limit} orders/hour: {user_orders_hour}')
        
        # Orders per day by user
        day_ago = now - timedelta(days=1)
        user_orders_day = user.orders.filter(created_at__gte=day_ago).count()
        limit = self.DEFAULT_VELOCITY_LIMITS['orders_per_day_user']
        if user_orders_day >= limit:
            result['risk_score'] += 20
            result['issues'].append(f'User exceeded {limit} orders/day: {user_orders_day}')
        
        # Amount per hour by user
        user_amount_hour = user.orders.filter(
            created_at__gte=hour_ago
        ).aggregate(total=Sum('total'))['total'] or Decimal('0')
        limit = self.DEFAULT_VELOCITY_LIMITS['amount_per_hour_user']
        if user_amount_hour + amount > limit:
            result['risk_score'] += 25
            result['issues'].append(f'User amount/hour exceeds {limit}')
        
        # Orders per hour by IP
        if ip_address:
            ip_orders_hour = self._get_velocity_count(
                VelocityCounter.CounterType.ORDER_BY_IP,
                ip_address,
                hour_ago
            )
            limit = self.DEFAULT_VELOCITY_LIMITS['orders_per_hour_ip']
            if ip_orders_hour >= limit:
                result['risk_score'] += 40
                result['issues'].append(f'IP exceeded {limit} orders/hour: {ip_orders_hour}')
            
            # Update velocity counter
            self._increment_velocity(
                VelocityCounter.CounterType.ORDER_BY_IP,
                ip_address,
                amount
            )
        
        # Update user velocity counter
        self._increment_velocity(
            VelocityCounter.CounterType.ORDER_BY_USER,
            str(user.id),
            amount
        )
        
        return result
    
    def _get_velocity_count(
        self,
        counter_type: str,
        identifier: str,
        since: 'datetime'
    ) -> int:
        """Get velocity count since a given time."""
        count = VelocityCounter.objects.filter(
            counter_type=counter_type,
            identifier=identifier,
            window_end__gte=since
        ).aggregate(total=Sum('count'))['total']
        return count or 0
    
    def _increment_velocity(
        self,
        counter_type: str,
        identifier: str,
        amount: Decimal = Decimal('0')
    ):
        """Increment velocity counter."""
        now = timezone.now()
        # Use hourly windows
        window_start = now.replace(minute=0, second=0, microsecond=0)
        window_end = window_start + timedelta(hours=1)
        
        counter, _ = VelocityCounter.objects.get_or_create(
            counter_type=counter_type,
            identifier=identifier,
            window_start=window_start,
            defaults={'window_end': window_end}
        )
        counter.count += 1
        counter.total_amount += amount
        counter.save(update_fields=['count', 'total_amount'])
    
    def _check_amount(self, user, amount: Decimal) -> dict:
        """Check order amount patterns."""
        result = {'risk_score': 0, 'issues': []}
        
        # First order with high amount
        if user.orders.count() == 0 and amount > Decimal('10000000'):  # 10M VND
            result['risk_score'] += 20
            result['issues'].append('First order with high amount')
        
        # Amount much higher than user average
        avg_order = user.orders.aggregate(avg=Avg('total'))['avg']
        if avg_order and amount > avg_order * 5:
            result['risk_score'] += 15
            result['issues'].append('Amount 5x higher than user average')
        
        # Very high amount regardless
        if amount > Decimal('50000000'):  # 50M VND
            result['risk_score'] += 10
            result['issues'].append('Very high order amount')
        
        return result
    
    def _check_user_behavior(self, user) -> dict:
        """Check user behavioral patterns."""
        result = {'risk_score': 0, 'issues': []}
        
        # New account
        account_age = timezone.now() - user.date_joined
        if account_age < timedelta(hours=1):
            result['risk_score'] += 20
            result['issues'].append('Account less than 1 hour old')
        elif account_age < timedelta(days=1):
            result['risk_score'] += 10
            result['issues'].append('Account less than 1 day old')
        
        # Unverified email
        if hasattr(user, 'email_verified') and not user.email_verified:
            result['risk_score'] += 15
            result['issues'].append('Email not verified')
        
        # High chargeback/refund rate
        if hasattr(user, 'orders'):
            total_orders = user.orders.count()
            if total_orders >= 5:
                refunded = user.orders.filter(status='refunded').count()
                refund_rate = refunded / total_orders
                if refund_rate > 0.3:
                    result['risk_score'] += 25
                    result['issues'].append(f'High refund rate: {refund_rate:.0%}')
        
        return result
    
    def _evaluate_rule(self, rule: FraudRule, order, user, context: dict) -> dict:
        """Evaluate a custom fraud rule."""
        result = {'matched': False, 'matched_value': '', 'rule_name': rule.name}
        
        conditions = rule.conditions
        
        # Example rule evaluations based on conditions
        if rule.rule_type == FraudRule.RuleType.AMOUNT:
            threshold = conditions.get('max_amount')
            if threshold and order.total > Decimal(str(threshold)):
                result['matched'] = True
                result['matched_value'] = str(order.total)
        
        elif rule.rule_type == FraudRule.RuleType.VELOCITY:
            # Custom velocity rules handled here
            pass
        
        elif rule.rule_type == FraudRule.RuleType.BLACKLIST:
            # Custom blacklist checks
            pass
        
        return result
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Quick check if IP is blocked."""
        cache_key = f'ip_blocked:{ip_address}'
        blocked = cache.get(cache_key)
        
        if blocked is None:
            try:
                blacklist = IPBlacklist.objects.get(ip_address=ip_address)
                blocked = blacklist.is_active
            except IPBlacklist.DoesNotExist:
                blocked = False
            cache.set(cache_key, blocked, 60)  # 1 minute cache
        
        return blocked
    
    def block_ip(
        self,
        ip_address: str,
        reason: str,
        notes: str = '',
        expires_hours: int = None,
        created_by=None
    ) -> IPBlacklist:
        """Add IP to blacklist."""
        expires_at = None
        if expires_hours:
            expires_at = timezone.now() + timedelta(hours=expires_hours)
        
        blacklist, created = IPBlacklist.objects.update_or_create(
            ip_address=ip_address,
            defaults={
                'reason': reason,
                'notes': notes,
                'expires_at': expires_at,
                'created_by': created_by
            }
        )
        
        # Clear cache
        cache.delete(f'ip_blocked:{ip_address}')
        
        logger.warning(f"IP blocked: {ip_address}, reason: {reason}")
        return blacklist
