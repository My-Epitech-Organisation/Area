"""
Custom permissions for the AREA project.

This module provides custom permission classes for Django REST Framework,
including email verification requirements as per project specifications.
"""

from rest_framework import permissions


class IsEmailVerified(permissions.BasePermission):
    """
    Permission that requires user to have verified their email address.
    
    As per project requirements:
    "The registered user then confirms their enrollment on the application 
    before being able to use it"
    
    This permission should be used in combination with IsAuthenticated.
    """

    message = (
        "Email verification required. Please verify your email address "
        "before using the application. Check your inbox for the verification link."
    )

    def has_permission(self, request, view):
        """
        Check if user has verified their email.
        
        Returns:
            bool: True if user is authenticated and email is verified
        """
        # User must be authenticated (should be checked by IsAuthenticated first)
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers and staff always have permission (for admin access)
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # Check if email is verified
        return getattr(request.user, 'email_verified', False)


class IsAuthenticatedAndVerified(permissions.BasePermission):
    """
    Combined permission: User must be authenticated AND have verified email.
    
    This is the standard permission for protected endpoints in AREA.
    Use this instead of IsAuthenticated for endpoints that require email verification.
    """

    def has_permission(self, request, view):
        """Check authentication and email verification."""
        # First check authentication
        if not request.user or not request.user.is_authenticated:
            self.message = "Authentication credentials were not provided."
            return False
        
        # Superusers and staff bypass email verification
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # Check email verification
        if not getattr(request.user, 'email_verified', False):
            self.message = (
                "Email verification required. Please verify your email address "
                "before using the application. Check your inbox for the verification link "
                "or request a new one at /auth/resend-verification/"
            )
            return False
        
        return True


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Allow authenticated users full access, others read-only.
    Email verification is NOT required for read-only access.
    """

    def has_permission(self, request, view):
        """Check if request should be permitted."""
        # Read-only access for anyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write access requires authentication (but not email verification)
        return request.user and request.user.is_authenticated
