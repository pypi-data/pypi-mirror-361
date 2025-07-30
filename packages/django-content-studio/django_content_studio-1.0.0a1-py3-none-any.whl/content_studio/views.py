from django.contrib import admin
from django.urls import reverse, NoReverseMatch
from django.views.generic import TemplateView
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .admin import AdminSerializer, admin_site
from .models import ModelSerializer
from .serializers import CurrentUserSerializer


class ContentStudioWebAppView(TemplateView):
    """
    View for rendering the content studio web app.
    """

    template_name = "content_studio/index.html"


class AdminApiViewSet(ViewSet):
    """
    Viewset for special admin endpoints.
    """

    permission_classes = [IsAdminUser]
    renderer_classes = [JSONRenderer]

    @action(
        methods=["get"],
        detail=False,
        url_path="info",
        permission_classes=[AllowAny],
    )
    def info(self, request):
        """
        Returns public information about the Content Studio admin.
        """

        data = {
            "site_header": admin_site.site_header,
            "site_title": admin_site.site_title,
            "index_title": admin_site.index_title,
            "site_url": admin_site.site_url,
            "health_check": get_health_check_path(),
            "login_backends": [
                backend.get_info()
                for backend in admin_site.login_backend.active_backends
            ],
            "token_backend": admin_site.token_backend.active_backend.get_info(),
        }

        return Response(data=data)

    @action(
        methods=["get"],
        detail=False,
        url_path="discover",
    )
    def discover(
        self,
        request,
    ):
        """
        Returns information about the Django app (models, admin models, admin site, settings, etc.).
        """
        data = {"models": []}
        registered_models = admin.site._registry

        for model, admin_class in registered_models.items():
            data["models"].append(
                {
                    **ModelSerializer(model).serialize(),
                    "admin": AdminSerializer(admin_class).serialize(request),
                }
            )

        return Response(data=data)

    @action(methods=["get"], detail=False, url_path="me")
    def me(self, request):
        """
        Returns information about the current user.
        """
        return Response(CurrentUserSerializer(request.user).data)


def get_health_check_path():
    try:
        return reverse("healthcheck")
    except NoReverseMatch:
        return None
