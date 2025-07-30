from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import MethodNotAllowed, NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.renderers import JSONRenderer
from rest_framework.viewsets import ModelViewSet

from .admin import admin_site
from .settings import cs_settings


class BaseModelViewSet(ModelViewSet):
    lookup_field = "id"
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    permission_classes = [DjangoModelPermissions]
    pagination_class = [PageNumberPagination]
    filter_backends = [SearchFilter, OrderingFilter]

    def __init__(self):
        super(BaseModelViewSet, self).__init__()

        self.authentication_classes = [
            admin_site.auth_backend.active_backend.authentication_class
        ]

    def retrieve(self, request, *args, **kwargs):
        """
        Disable this endpoint for singletons. They should use
        the list endpoint instead.
        """
        if self.is_singleton:
            raise MethodNotAllowed(
                method="GET",
                detail="Singleton objects do not support the retrieve endpoint.",
            )

        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        We overwrite the update method to support singletons. If a singleton
        doesn't exist it will be created.
        """
        if self.is_singleton:
            try:
                super().update(request, *args, **kwargs)
            except NotFound:
                self.create(request, *args, **kwargs)

        return super().update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        We overwrite the list method to support singletons. If a singleton
        doesn't exist this will raise a NotFound exception.
        """
        if self.is_singleton:
            return super().retrieve(request, *args, **kwargs)

        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save()

        if hasattr(instance, cs_settings.CREATED_BY):
            setattr(instance, cs_settings.CREATED_BY, self.request.user)
            instance.save()

        content_type = ContentType.objects.get_for_model(instance)
        LogEntry.objects.create(
            user=self.request.user,
            action_flag=ADDITION,
            content_type=content_type,
            object_id=instance.id,
            object_repr=str(instance)[:200],
            change_message="",
        )

    def perform_update(self, serializer):
        instance = serializer.save()

        if hasattr(instance, cs_settings.EDITED_BY):
            setattr(instance, cs_settings.EDITED_BY, self.request.user)
            instance.save()

        content_type = ContentType.objects.get_for_model(instance)
        LogEntry.objects.create(
            user=self.request.user,
            action_flag=CHANGE,
            content_type=content_type,
            object_id=instance.id,
            object_repr=str(instance)[:200],
            change_message="",
        )

    def perform_destroy(self, instance):
        content_type = ContentType.objects.get_for_model(instance)
        LogEntry.objects.create(
            user=self.request.user,
            action_flag=DELETION,
            content_type=content_type,
            object_id=instance.id,
            object_repr=str(instance)[:200],
            change_message="",
        )

        instance.delete()

    def get_object(self):
        """
        We overwrite this method to add support for singletons.
        If a singleton doesn't exist it will raise a NotFound exception.
        """
        if self.is_singleton:
            try:
                return self.get_queryset().get()
            except self.queryset.model.DoesNotExist:
                raise NotFound()

        return super().get_object()

    @property
    def is_singleton(self):
        return getattr(self.get_queryset().model, "is_singleton", False)
