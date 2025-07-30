from django.urls import re_path

from .router import content_studio_router
from .views import ContentStudioWebAppView, AdminApiViewSet

content_studio_router.register("api", AdminApiViewSet, "content_studio_admin")

urlpatterns = content_studio_router.urls + [
    re_path(
        "^(?!api).*$", ContentStudioWebAppView.as_view(), name="content_studio_web"
    ),
]
