"""
Custom User Model for Owls E-commerce Platform
===============================================
Professional user model with email-based authentication,
role management, and comprehensive profile features.
"""

import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from apps.base.core.system.models import TimeStampedModel, MetaDataModel


class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', User.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel, MetaDataModel):
    """
    Custom User model for Owls E-commerce Platform.
    Uses email for authentication instead of username.
    """
    
    class Role(models.TextChoices):
        """User role choices."""
        CUSTOMER = 'customer', _('Customer')
        VENDOR = 'vendor', _('Vendor')
        DRIVER = 'driver', _('Driver')
        SUPPORT = 'support', _('Support Staff')
        MODERATOR = 'moderator', _('Moderator')
        ADMIN = 'admin', _('Administrator')
    
    class Gender(models.TextChoices):
        """Gender choices."""
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHER = 'other', _('Other')
        PREFER_NOT_TO_SAY = 'prefer_not_to_say', _('Prefer not to say')

    # Primary fields
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(
        _('Email address'),
        unique=True,
        db_index=True,
        max_length=255
    )
    
    # Phone validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_('Phone number must be in format: +999999999. Up to 15 digits allowed.')
    )
    phone_number = models.CharField(
        _('Phone number'),
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        unique=True,
        db_index=True
    )
    
    # Personal information
    first_name = models.CharField(_('First name'), max_length=150, blank=True)
    last_name = models.CharField(_('Last name'), max_length=150, blank=True)
    avatar = models.ImageField(
        _('Avatar'),
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(_('Date of birth'), blank=True, null=True)
    gender = models.CharField(
        _('Gender'),
        max_length=20,
        choices=Gender.choices,
        blank=True
    )
    
    # Role and permissions
    role = models.CharField(
        _('Role'),
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        db_index=True
    )
    
    # Status flags
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active.')
    )
    is_staff = models.BooleanField(
        _('Staff status'),
        default=False,
        help_text=_('Designates whether the user can log into admin site.')
    )
    is_verified = models.BooleanField(
        _('Verified'),
        default=False,
        help_text=_('Designates whether the user has verified their email.')
    )
    is_phone_verified = models.BooleanField(
        _('Phone verified'),
        default=False
    )
    
    # Activity tracking
    last_login = models.DateTimeField(_('Last login'), blank=True, null=True)
    last_activity = models.DateTimeField(_('Last activity'), blank=True, null=True)
    date_joined = models.DateTimeField(_('Date joined'), default=timezone.now)
    
    # Marketing preferences
    email_notifications = models.BooleanField(_('Email notifications'), default=True)
    sms_notifications = models.BooleanField(_('SMS notifications'), default=False)
    push_notifications = models.BooleanField(_('Push notifications'), default=True)
    
    # Reference fields (for analytics)
    referral_code = models.CharField(
        _('Referral code'),
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='referrals',
        blank=True,
        null=True
    )
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email & Password required by default

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['phone_number']),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return user's full name."""
        return f'{self.first_name} {self.last_name}'.strip() or self.email

    def get_short_name(self):
        """Return first name or email prefix."""
        return self.first_name or self.email.split('@')[0]

    def save(self, *args, **kwargs):
        """Generate referral code on first save."""
        if not self.referral_code:
            self.referral_code = self._generate_referral_code()
        super().save(*args, **kwargs)

    def _generate_referral_code(self):
        """Generate a unique referral code."""
        import string
        import random
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        while User.objects.filter(referral_code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return code

    # Role check methods
    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    @property
    def is_vendor(self):
        return self.role == self.Role.VENDOR

    @property
    def is_driver(self):
        return self.role == self.Role.DRIVER

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser


class UserAddress(TimeStampedModel):
    """
    User delivery/billing addresses.
    """
    
    class AddressType(models.TextChoices):
        HOME = 'home', _('Home')
        OFFICE = 'office', _('Office')
        OTHER = 'other', _('Other')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    address_type = models.CharField(
        _('Address type'),
        max_length=20,
        choices=AddressType.choices,
        default=AddressType.HOME
    )
    
    # Contact
    recipient_name = models.CharField(_('Recipient name'), max_length=255)
    phone_number = models.CharField(_('Phone number'), max_length=17)
    
    # Address details
    street_address = models.CharField(_('Street address'), max_length=500)
    apartment = models.CharField(_('Apartment/Unit'), max_length=100, blank=True)
    ward = models.CharField(_('Ward'), max_length=100, blank=True)
    district = models.CharField(_('District'), max_length=100)
    city = models.CharField(_('City/Province'), max_length=100)
    country = models.CharField(_('Country'), max_length=100, default='Vietnam')
    postal_code = models.CharField(_('Postal code'), max_length=20, blank=True)
    
    # Coordinates (for delivery optimization)
    latitude = models.DecimalField(
        _('Latitude'),
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )
    longitude = models.DecimalField(
        _('Longitude'),
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )
    
    # Flags
    is_default = models.BooleanField(_('Default address'), default=False)
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        verbose_name = _('User Address')
        verbose_name_plural = _('User Addresses')
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f'{self.recipient_name} - {self.street_address}, {self.city}'

    def save(self, *args, **kwargs):
        """Ensure only one default address per user."""
        if self.is_default:
            UserAddress.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def full_address(self):
        """Return formatted full address."""
        parts = [self.street_address]
        if self.apartment:
            parts.append(self.apartment)
        if self.ward:
            parts.append(self.ward)
        parts.extend([self.district, self.city])
        if self.postal_code:
            parts.append(self.postal_code)
        parts.append(self.country)
        return ', '.join(parts)


class UserVerification(TimeStampedModel):
    """
    User verification tokens for email/phone verification, password reset.
    """
    
    class VerificationType(models.TextChoices):
        EMAIL = 'email', _('Email Verification')
        PHONE = 'phone', _('Phone Verification')
        PASSWORD_RESET = 'password_reset', _('Password Reset')
        TWO_FACTOR = 'two_factor', _('Two Factor Authentication')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='verifications'
    )
    verification_type = models.CharField(
        _('Verification type'),
        max_length=20,
        choices=VerificationType.choices
    )
    token = models.CharField(_('Token'), max_length=255, unique=True)
    code = models.CharField(_('Code'), max_length=10, blank=True)  # For OTP
    expires_at = models.DateTimeField(_('Expires at'))
    is_used = models.BooleanField(_('Is used'), default=False)
    used_at = models.DateTimeField(_('Used at'), blank=True, null=True)

    class Meta:
        verbose_name = _('User Verification')
        verbose_name_plural = _('User Verifications')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.verification_type}'

    @property
    def is_expired(self):
        """Check if token has expired."""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """Check if token is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired


class UserSession(TimeStampedModel):
    """
    Track user sessions for security monitoring.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    session_key = models.CharField(_('Session key'), max_length=255, unique=True)
    device_type = models.CharField(_('Device type'), max_length=50, blank=True)
    device_name = models.CharField(_('Device name'), max_length=255, blank=True)
    browser = models.CharField(_('Browser'), max_length=100, blank=True)
    os = models.CharField(_('Operating system'), max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(_('IP address'), blank=True, null=True)
    location = models.CharField(_('Location'), max_length=255, blank=True)
    last_activity = models.DateTimeField(_('Last activity'), auto_now=True)
    is_active = models.BooleanField(_('Is active'), default=True)

    class Meta:
        verbose_name = _('User Session')
        verbose_name_plural = _('User Sessions')
        ordering = ['-last_activity']

    def __str__(self):
        return f'{self.user.email} - {self.device_type}'
