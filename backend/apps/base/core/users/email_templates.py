"""
Email Templates for Owls E-commerce Platform
=============================================
Centralized email content strings for easy maintenance and i18n support.

Usage:
    from apps.base.core.users.email_templates import EmailTemplates
    
    subject = EmailTemplates.PASSWORD_RESET_SUBJECT
    message = EmailTemplates.format_password_reset(user_name, reset_url)
"""

from django.conf import settings
from django.utils.translation import gettext_lazy as _


class EmailTemplates:
    """
    Centralized email template strings.
    
    All hardcoded email text is stored here for:
    1. Easy maintenance - single place to update
    2. i18n support - wrap in gettext for translation
    3. Consistency - same wording across the platform
    """
    
    # ========================================
    # Password Reset
    # ========================================
    
    PASSWORD_RESET_SUBJECT = _('Đặt lại mật khẩu - Owls')
    
    PASSWORD_RESET_TEMPLATE = _('''Xin chào {user_name},

Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản Owls.

Nhấp vào liên kết sau để đặt lại mật khẩu:
{reset_url}

Liên kết này sẽ hết hạn sau 1 giờ.

Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.

Trân trọng,
Đội ngũ Owls''')
    
    @classmethod
    def format_password_reset(cls, user_name: str, reset_url: str) -> str:
        """Format password reset email message."""
        return str(cls.PASSWORD_RESET_TEMPLATE).format(
            user_name=user_name,
            reset_url=reset_url
        )
    
    # ========================================
    # Welcome Email
    # ========================================
    
    @classmethod
    def get_welcome_subject(cls) -> str:
        """Get welcome email subject with site name."""
        return _('Chào mừng bạn đến với {site_name}!').format(
            site_name=settings.SITE_NAME
        )
    
    WELCOME_TEMPLATE = _('''Xin chào {user_name},

Cảm ơn bạn đã đăng ký tài khoản tại {site_name}!

Bạn có thể bắt đầu mua sắm ngay bây giờ với hàng ngàn sản phẩm chất lượng từ các nhà cung cấp uy tín.

Nếu bạn có bất kỳ câu hỏi nào, đừng ngần ngại liên hệ với chúng tôi.

Trân trọng,
Đội ngũ {site_name}''')
    
    @classmethod
    def format_welcome(cls, user_name: str) -> str:
        """Format welcome email message."""
        return str(cls.WELCOME_TEMPLATE).format(
            user_name=user_name,
            site_name=settings.SITE_NAME
        )
    
    # ========================================
    # Email Verification
    # ========================================
    
    @classmethod
    def get_verification_subject(cls) -> str:
        """Get email verification subject with site name."""
        return _('Xác nhận email - {site_name}').format(
            site_name=settings.SITE_NAME
        )
    
    VERIFICATION_TEMPLATE = _('''Xin chào {user_name},

Vui lòng nhấp vào liên kết sau để xác nhận địa chỉ email của bạn:
{verification_url}

Liên kết này sẽ hết hạn sau 24 giờ.

Trân trọng,
Đội ngũ {site_name}''')
    
    @classmethod
    def format_verification(cls, user_name: str, verification_url: str) -> str:
        """Format verification email message."""
        return str(cls.VERIFICATION_TEMPLATE).format(
            user_name=user_name,
            verification_url=verification_url,
            site_name=settings.SITE_NAME
        )
    
    # ========================================
    # Order Confirmation
    # ========================================
    
    @classmethod
    def get_order_confirmation_subject(cls, order_number: str) -> str:
        """Get order confirmation subject."""
        return _('Xác nhận đơn hàng #{order_number} - {site_name}').format(
            order_number=order_number,
            site_name=settings.SITE_NAME
        )
    
    ORDER_CONFIRMATION_TEMPLATE = _('''Xin chào {user_name},

Cảm ơn bạn đã đặt hàng tại {site_name}!

Mã đơn hàng: {order_number}
Tổng tiền: {total} VNĐ

Trạng thái: {status}

Chúng tôi sẽ thông báo khi đơn hàng được vận chuyển.

Trân trọng,
Đội ngũ {site_name}''')
    
    @classmethod
    def format_order_confirmation(
        cls, 
        user_name: str, 
        order_number: str, 
        total: str,
        status: str
    ) -> str:
        """Format order confirmation email message."""
        return str(cls.ORDER_CONFIRMATION_TEMPLATE).format(
            user_name=user_name,
            order_number=order_number,
            total=total,
            status=status,
            site_name=settings.SITE_NAME
        )
    
    # ========================================
    # Order Shipped
    # ========================================
    
    @classmethod
    def get_order_shipped_subject(cls, order_number: str) -> str:
        """Get shipping notification subject."""
        return _('Đơn hàng #{order_number} đang được vận chuyển - {site_name}').format(
            order_number=order_number,
            site_name=settings.SITE_NAME
        )
    
    ORDER_SHIPPED_TEMPLATE = _('''Xin chào {user_name},

Đơn hàng #{order_number} của bạn đã được giao cho đơn vị vận chuyển.{tracking_info}

Địa chỉ giao hàng:
{shipping_name}
{shipping_address}
{shipping_city}

Bạn sẽ nhận được hàng trong vài ngày tới.

Trân trọng,
Đội ngũ {site_name}''')
    
    @classmethod
    def format_order_shipped(
        cls,
        user_name: str,
        order_number: str,
        shipping_name: str,
        shipping_address: str,
        shipping_city: str,
        tracking_number: str = ''
    ) -> str:
        """Format shipping notification email message."""
        tracking_info = ''
        if tracking_number:
            tracking_info = f'\nMã vận đơn: {tracking_number}'
        
        return str(cls.ORDER_SHIPPED_TEMPLATE).format(
            user_name=user_name,
            order_number=order_number,
            tracking_info=tracking_info,
            shipping_name=shipping_name,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            site_name=settings.SITE_NAME
        )
    
    # ========================================
    # Order Cancelled
    # ========================================
    
    @classmethod
    def get_order_cancelled_subject(cls, order_number: str) -> str:
        """Get order cancellation subject."""
        return _('Đơn hàng #{order_number} đã bị hủy - {site_name}').format(
            order_number=order_number,
            site_name=settings.SITE_NAME
        )
    
    ORDER_CANCELLED_TEMPLATE = _('''Xin chào {user_name},

Đơn hàng #{order_number} của bạn đã bị hủy.

Lý do: {reason}

Nếu bạn đã thanh toán, số tiền sẽ được hoàn lại trong 5-7 ngày làm việc.

Nếu bạn có bất kỳ thắc mắc nào, vui lòng liên hệ bộ phận hỗ trợ.

Trân trọng,
Đội ngũ {site_name}''')
    
    @classmethod
    def format_order_cancelled(
        cls,
        user_name: str,
        order_number: str,
        reason: str
    ) -> str:
        """Format order cancellation email message."""
        return str(cls.ORDER_CANCELLED_TEMPLATE).format(
            user_name=user_name,
            order_number=order_number,
            reason=reason,
            site_name=settings.SITE_NAME
        )


# Convenience aliases for backward compatibility
PASSWORD_RESET_SUBJECT = EmailTemplates.PASSWORD_RESET_SUBJECT
format_password_reset = EmailTemplates.format_password_reset
format_welcome = EmailTemplates.format_welcome
format_verification = EmailTemplates.format_verification
format_order_confirmation = EmailTemplates.format_order_confirmation
format_order_shipped = EmailTemplates.format_order_shipped
