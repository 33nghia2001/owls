"""
User Celery Tasks for Owls E-commerce Platform
==============================================
Asynchronous tasks for user-related operations.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

from .email_templates import EmailTemplates

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
    name='users.send_password_reset_email'
)
def send_password_reset_email_task(self, email: str, user_name: str, reset_url: str):
    """
    Send password reset email asynchronously.
    
    Args:
        email: User's email address
        user_name: User's display name
        reset_url: Password reset URL with token
    """
    try:
        subject = str(EmailTemplates.PASSWORD_RESET_SUBJECT)
        message = EmailTemplates.format_password_reset(user_name, reset_url)

        # Try to use HTML template if available
        html_message = None
        try:
            html_message = render_to_string('emails/password_reset.html', {
                'user_name': user_name,
                'reset_url': reset_url,
                'site_name': settings.SITE_NAME,
            })
        except Exception:
            # Template not found, use plain text only
            pass

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent successfully to {email}")
        return {'status': 'success', 'email': email}
        
    except Exception as exc:
        logger.error(f"Failed to send password reset email to {email}: {exc}")
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
    name='users.send_welcome_email'
)
def send_welcome_email_task(self, email: str, user_name: str):
    """
    Send welcome email to new users.
    
    Args:
        email: User's email address
        user_name: User's display name
    """
    try:
        subject = EmailTemplates.get_welcome_subject()
        message = EmailTemplates.format_welcome(user_name)

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent successfully to {email}")
        return {'status': 'success', 'email': email}
        
    except Exception as exc:
        logger.error(f"Failed to send welcome email to {email}: {exc}")
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
    name='users.send_verification_email'
)
def send_verification_email_task(self, email: str, user_name: str, verification_url: str):
    """
    Send email verification link.
    
    Args:
        email: User's email address
        user_name: User's display name
        verification_url: Email verification URL
    """
    try:
        subject = EmailTemplates.get_verification_subject()
        message = EmailTemplates.format_verification(user_name, verification_url)

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent successfully to {email}")
        return {'status': 'success', 'email': email}
        
    except Exception as exc:
        logger.error(f"Failed to send verification email to {email}: {exc}")
        raise self.retry(exc=exc)


@shared_task(name='users.cleanup_expired_sessions')
def cleanup_expired_sessions_task():
    """
    Periodic task to cleanup expired user sessions.
    Should be scheduled via Celery Beat.
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models import UserSession
    
    try:
        # Delete sessions that are:
        # 1. Inactive (is_active=False)
        # 2. Last activity more than 30 days ago
        cutoff_date = timezone.now() - timedelta(days=30)
        
        deleted_count, _ = UserSession.objects.filter(
            is_active=False
        ).delete()
        
        deleted_old, _ = UserSession.objects.filter(
            last_activity__lt=cutoff_date
        ).delete()
        
        total_deleted = deleted_count + deleted_old
        logger.info(f"Cleaned up {total_deleted} expired sessions")
        
        return {'status': 'success', 'deleted': total_deleted}
        
    except Exception as exc:
        logger.error(f"Failed to cleanup sessions: {exc}")
        raise


@shared_task(name='users.cleanup_unverified_users')
def cleanup_unverified_users_task():
    """
    Periodic task to cleanup users who haven't verified email after 7 days.
    Should be scheduled via Celery Beat.
    """
    from django.utils import timezone
    from datetime import timedelta
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    try:
        cutoff_date = timezone.now() - timedelta(days=7)
        
        # Delete unverified users older than 7 days
        # who have no orders (to avoid deleting real customers)
        deleted_count, _ = User.objects.filter(
            is_verified=False,
            date_joined__lt=cutoff_date,
            orders__isnull=True  # No orders
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} unverified users")
        
        return {'status': 'success', 'deleted': deleted_count}
        
    except Exception as exc:
        logger.error(f"Failed to cleanup unverified users: {exc}")
        raise
