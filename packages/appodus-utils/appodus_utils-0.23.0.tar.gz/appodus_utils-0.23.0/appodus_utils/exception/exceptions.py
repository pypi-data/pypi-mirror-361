from typing import Optional, TypedDict
from fastapi import status


class ExceptionContext(TypedDict, total=False):
    """
    Structured metadata optionally attached to exceptions
    to provide context during logging, monitoring, or debugging.
    """
    user_id: str
    email: str
    project_id: str
    order_id: str
    feature: str
    service: str
    limit_type: str
    endpoint: str
    payload: dict
    reason: str
    resource: str


class AppodusBaseException(Exception):
    """
    Base class for all Appodus exceptions.

    Attributes:
        message (str): Human-readable error message.
        status_code (int): HTTP status code to return in API response.
        code (str): Machine-readable error identifier.
        context (ExceptionContext): Optional dictionary providing structured metadata.
    """
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str = "APPODUS_ERROR",
        context: Optional[ExceptionContext] = None
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.context = context or ExceptionContext()
        super().__init__(message)


# ────────────────────────────────
# Authentication & Authorization
# ────────────────────────────────

class UnauthorizedException(AppodusBaseException):
    def __init__(self):
        super().__init__("Unauthorized access", status.HTTP_401_UNAUTHORIZED, "UNAUTHORIZED")


class ForbiddenException(AppodusBaseException):
    def __init__(self):
        super().__init__("Forbidden action", status.HTTP_403_FORBIDDEN, "FORBIDDEN")


class InvalidTokenException(AppodusBaseException):
    def __init__(self):
        super().__init__("Invalid or expired token", status.HTTP_401_UNAUTHORIZED, "INVALID_TOKEN")


class InvalidCredentialsException(AppodusBaseException):
    def __init__(self):
        super().__init__("Invalid username or password", status.HTTP_401_UNAUTHORIZED, "INVALID_CREDENTIALS")


# ────────────────────────────────
# User Management
# ────────────────────────────────

class UserNotFoundException(AppodusBaseException):
    def __init__(self, user_id: str):
        super().__init__(
            message=f"User with ID {user_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            code="USER_NOT_FOUND",
            context=ExceptionContext(user_id=user_id)
        )


class UserAlreadyExistsException(AppodusBaseException):
    def __init__(self, email: str):
        super().__init__(
            message=f"User with email {email} already exists",
            status_code=status.HTTP_409_CONFLICT,
            code="USER_ALREADY_EXISTS",
            context=ExceptionContext(email=email)
        )


# ────────────────────────────────
# Resource / CRUD Operations
# ────────────────────────────────

class ResourceNotFoundException(AppodusBaseException):
    def __init__(self, resource: str):
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            code="RESOURCE_NOT_FOUND",
            context=ExceptionContext(resource=resource)
        )


class ResourceConflictException(AppodusBaseException):
    def __init__(self, resource: str):
        super().__init__(
            message=f"Conflict while creating/updating {resource}",
            status_code=status.HTTP_409_CONFLICT,
            code="RESOURCE_CONFLICT",
            context=ExceptionContext(resource=resource)
        )


class InvalidResourceStateException(AppodusBaseException):
    def __init__(self, resource: str):
        super().__init__(
            message=f"{resource} is in an invalid state",
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_RESOURCE_STATE",
            context=ExceptionContext(resource=resource)
        )


# ────────────────────────────────
# Validation
# ────────────────────────────────

class ValidationException(AppodusBaseException):
    def __init__(self, errors: list, context: Optional[ExceptionContext] = None):
        super().__init__(
            message="Validation failed",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            context=context
        )
        self.details = errors


# ────────────────────────────────
# System / Server Errors
# ────────────────────────────────

class InternalServerException(AppodusBaseException):
    def __init__(self):
        super().__init__("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "INTERNAL_ERROR")


class DependencyException(AppodusBaseException):
    def __init__(self, service: str):
        super().__init__(
            message=f"Failed dependency: {service}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="DEPENDENCY_FAILURE",
            context=ExceptionContext(service=service)
        )


# ────────────────────────────────
# Integration / External APIs
# ────────────────────────────────

class ExternalAPIException(AppodusBaseException):
    def __init__(self, service: str):
        super().__init__(
            message=f"{service} API returned an error",
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="EXTERNAL_API_ERROR",
            context=ExceptionContext(service=service)
        )


class TimeoutException(AppodusBaseException):
    def __init__(self, service: str):
        super().__init__(
            message=f"Timeout while calling {service}",
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            code="TIMEOUT_ERROR",
            context=ExceptionContext(service=service)
        )


# ────────────────────────────────
# Payments / Finance
# ────────────────────────────────

class PaymentFailedException(AppodusBaseException):
    def __init__(self, reason: str):
        super().__init__(
            message=f"Payment failed: {reason}",
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            code="PAYMENT_FAILED",
            context=ExceptionContext(reason=reason)
        )


class InvalidCardException(AppodusBaseException):
    def __init__(self):
        super().__init__("Invalid card details", status.HTTP_400_BAD_REQUEST, "INVALID_CARD")


class SubscriptionRequiredException(AppodusBaseException):
    def __init__(self):
        super().__init__("Subscription required to access this feature", status.HTTP_402_PAYMENT_REQUIRED, "SUBSCRIPTION_REQUIRED")


# ────────────────────────────────
# Business Logic / Domain-Specific
# ────────────────────────────────

class PlanLimitExceededException(AppodusBaseException):
    def __init__(self, limit_type: str):
        super().__init__(
            message=f"{limit_type} limit exceeded for current plan",
            status_code=status.HTTP_403_FORBIDDEN,
            code="PLAN_LIMIT_EXCEEDED",
            context=ExceptionContext(limit_type=limit_type)
        )


class FeatureNotAvailableException(AppodusBaseException):
    def __init__(self, feature: str):
        super().__init__(
            message=f"{feature} is not available in your current plan",
            status_code=status.HTTP_403_FORBIDDEN,
            code="FEATURE_NOT_AVAILABLE",
            context=ExceptionContext(feature=feature)
        )


class OrderNotCancelableException(AppodusBaseException):
    def __init__(self, order_id: str):
        super().__init__(
            message=f"Order {order_id} cannot be canceled",
            status_code=status.HTTP_400_BAD_REQUEST,
            code="ORDER_NOT_CANCELABLE",
            context=ExceptionContext(order_id=order_id)
        )


class SellerVerificationRequiredException(AppodusBaseException):
    def __init__(self):
        super().__init__("Seller verification is required", status.HTTP_403_FORBIDDEN, "SELLER_NOT_VERIFIED")
