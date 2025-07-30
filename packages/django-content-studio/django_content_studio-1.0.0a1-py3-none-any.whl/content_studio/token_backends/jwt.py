from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class SimpleJwtViewSet(ViewSet):
    @action(
        detail=False, methods=["post"], permission_classes=[], authentication_classes=[]
    )
    def refresh(self, request):
        from rest_framework_simplejwt.views import TokenRefreshView

        view_instance = TokenRefreshView()
        view_instance.request = request
        view_instance.format_kwarg = None
        return view_instance.post(request)


class SimpleJwtBackend:
    name = "Simple JWT"
    authentication_class = None
    view_set = SimpleJwtViewSet

    def __init__(self):
        from rest_framework_simplejwt.authentication import JWTAuthentication

        self.authentication_class = JWTAuthentication

    @classmethod
    def get_info(cls):

        from rest_framework_simplejwt.settings import api_settings as simplejwt_settings

        return {
            "type": cls.__name__,
            "settings": {
                "ACCESS_TOKEN_LIFETIME": simplejwt_settings.ACCESS_TOKEN_LIFETIME.total_seconds(),
            },
        }

    @property
    def is_available(self) -> bool:
        try:
            import rest_framework_simplejwt

            return True
        except ImportError:
            return False

    @classmethod
    def get_response_for_user(cls, user):
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )
