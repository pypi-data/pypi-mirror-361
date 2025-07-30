from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.viewsets import ViewSet


class UsernamePasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UsernamePasswordViewSet(ViewSet):
    """
    View set for username and password endpoints.
    """

    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]

    def create(self, request):
        serializer = UsernamePasswordSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = UsernamePasswordBackend.login(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        if user is None or not user.is_active:
            raise PermissionDenied()

        from ..admin import admin_site

        return admin_site.auth_backend.active_backend.get_response_for_user(user)


class UsernamePasswordBackend:
    name = "Username password"
    view_set = UsernamePasswordViewSet

    @classmethod
    def get_info(cls):
        """
        Returns information about the backend.
        """
        user_model = get_user_model()
        username_field = getattr(user_model, user_model.USERNAME_FIELD, None)

        return {
            "type": cls.__name__,
            "config": {"username_field_type": username_field.field.__class__.__name__},
        }

    @classmethod
    def login(cls, username, password):
        """
        Authenticates user using username and password.
        Returns the user if successful, None otherwise.
        """
        return authenticate(username=username, password=password)

    def request_password_reset(self, username):
        """
        Sends a password reset email.
        """
        raise NotImplemented(
            "You need to implement a method for sending a password reset token."
        )

    def complete_password_reset(self, reset_token, new_password):
        """
        Sets the new password based on the reset token.
        """
        raise NotImplemented(
            "You need to implement a method for validating a reset token and setting a new password."
        )
