"""
Custom Exception Handlers for Owls E-commerce Platform
=======================================================
Provides consistent error responses across all API endpoints.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)


class OwlsBaseException(Exception):
    """Base exception for all Owls custom exceptions."""
    default_message = "An error occurred"
    default_code = "error"
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message=None, code=None, extra_data=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.extra_data = extra_data or {}
        super().__init__(self.message)


class ValidationError(OwlsBaseException):
    """Validation errors for business logic."""
    default_message = "Validation failed"
    default_code = "validation_error"
    status_code = status.HTTP_400_BAD_REQUEST


class NotFoundError(OwlsBaseException):
    """Resource not found errors."""
    default_message = "Resource not found"
    default_code = "not_found"
    status_code = status.HTTP_404_NOT_FOUND


class PermissionDeniedError(OwlsBaseException):
    """Permission denied errors."""
    default_message = "You do not have permission to perform this action"
    default_code = "permission_denied"
    status_code = status.HTTP_403_FORBIDDEN


class AuthenticationError(OwlsBaseException):
    """Authentication errors."""
    default_message = "Authentication failed"
    default_code = "authentication_failed"
    status_code = status.HTTP_401_UNAUTHORIZED


class ConflictError(OwlsBaseException):
    """Conflict errors (e.g., duplicate resources)."""
    default_message = "Resource conflict"
    default_code = "conflict"
    status_code = status.HTTP_409_CONFLICT


class RateLimitError(OwlsBaseException):
    """Rate limit exceeded errors."""
    default_message = "Too many requests. Please try again later."
    default_code = "rate_limit_exceeded"
    status_code = status.HTTP_429_TOO_MANY_REQUESTS


class ServiceUnavailableError(OwlsBaseException):
    """Service unavailable errors."""
    default_message = "Service temporarily unavailable"
    default_code = "service_unavailable"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


# E-commerce Specific Exceptions
class InsufficientStockError(OwlsBaseException):
    """Raised when product stock is insufficient."""
    default_message = "Insufficient stock available"
    default_code = "insufficient_stock"
    status_code = status.HTTP_400_BAD_REQUEST


class InsufficientBalanceError(OwlsBaseException):
    """Raised when wallet balance is insufficient."""
    default_message = "Insufficient balance"
    default_code = "insufficient_balance"
    status_code = status.HTTP_400_BAD_REQUEST


class PaymentError(OwlsBaseException):
    """Payment processing errors."""
    default_message = "Payment processing failed"
    default_code = "payment_failed"
    status_code = status.HTTP_402_PAYMENT_REQUIRED


class OrderError(OwlsBaseException):
    """Order processing errors."""
    default_message = "Order processing failed"
    default_code = "order_failed"
    status_code = status.HTTP_400_BAD_REQUEST


class CartError(OwlsBaseException):
    """Cart operation errors."""
    default_message = "Cart operation failed"
    default_code = "cart_error"
    status_code = status.HTTP_400_BAD_REQUEST


class VendorError(OwlsBaseException):
    """Vendor-related errors."""
    default_message = "Vendor operation failed"
    default_code = "vendor_error"
    status_code = status.HTTP_400_BAD_REQUEST


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework.
    Provides consistent error response format.
    """
    # Get the standard error response first
    response = exception_handler(exc, context)

    # Build consistent error response format
    error_data = {
        'success': False,
        'error': {
            'code': 'unknown_error',
            'message': 'An unexpected error occurred',
            'details': None
        }
    }

    # Handle Owls custom exceptions
    if isinstance(exc, OwlsBaseException):
        error_data['error'] = {
            'code': exc.code,
            'message': exc.message,
            'details': exc.extra_data or None
        }
        return Response(error_data, status=exc.status_code)

    # Handle DRF exceptions
    if response is not None:
        error_data['error'] = {
            'code': getattr(exc, 'default_code', 'api_error'),
            'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
            'details': response.data if isinstance(response.data, dict) else {'errors': response.data}
        }
        return Response(error_data, status=response.status_code)

    # Handle Django ValidationError
    if isinstance(exc, DjangoValidationError):
        error_data['error'] = {
            'code': 'validation_error',
            'message': 'Validation failed',
            'details': exc.message_dict if hasattr(exc, 'message_dict') else {'errors': exc.messages}
        }
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

    # Handle 404 errors
    if isinstance(exc, Http404):
        error_data['error'] = {
            'code': 'not_found',
            'message': str(exc) or 'Resource not found',
            'details': None
        }
        return Response(error_data, status=status.HTTP_404_NOT_FOUND)

    # Handle IntegrityError (duplicate key, etc.)
    if isinstance(exc, IntegrityError):
        logger.error(f"Database integrity error: {exc}")
        error_data['error'] = {
            'code': 'integrity_error',
            'message': 'Database constraint violated',
            'details': None
        }
        return Response(error_data, status=status.HTTP_409_CONFLICT)

    # Log unhandled exceptions
    logger.exception(f"Unhandled exception: {exc}")

    # Return generic error for unhandled exceptions (don't expose details)
    return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ErrorMessages:
    """Centralized error messages for consistency."""
    
    # Authentication
    INVALID_CREDENTIALS = "Invalid email or password"
    ACCOUNT_DISABLED = "Your account has been disabled"
    ACCOUNT_NOT_VERIFIED = "Please verify your email address"
    TOKEN_EXPIRED = "Token has expired"
    TOKEN_INVALID = "Invalid token"
    
    # User
    USER_NOT_FOUND = "User not found"
    EMAIL_ALREADY_EXISTS = "An account with this email already exists"
    PHONE_ALREADY_EXISTS = "An account with this phone number already exists"
    
    # Product
    PRODUCT_NOT_FOUND = "Product not found"
    PRODUCT_UNAVAILABLE = "Product is currently unavailable"
    PRODUCT_OUT_OF_STOCK = "Product is out of stock"
    
    # Cart
    CART_EMPTY = "Your cart is empty"
    CART_ITEM_NOT_FOUND = "Cart item not found"
    MAX_CART_ITEMS_REACHED = "Maximum cart items limit reached"
    
    # Order
    ORDER_NOT_FOUND = "Order not found"
    ORDER_CANNOT_BE_CANCELLED = "This order cannot be cancelled"
    ORDER_ALREADY_PROCESSED = "This order has already been processed"
    
    # Payment
    PAYMENT_FAILED = "Payment processing failed"
    PAYMENT_NOT_FOUND = "Payment not found"
    REFUND_NOT_ALLOWED = "Refund is not allowed for this order"
    
    # Vendor
    VENDOR_NOT_FOUND = "Vendor not found"
    VENDOR_NOT_APPROVED = "Vendor is not approved yet"
    VENDOR_SUSPENDED = "Vendor account is suspended"
    
    # General
    INVALID_REQUEST = "Invalid request"
    PERMISSION_DENIED = "Permission denied"
    RATE_LIMIT_EXCEEDED = "Too many requests. Please try again later."
