from django.contrib.admin import ModelAdmin, site
from django.db.models import Model
from rest_framework.permissions import IsAdminUser
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from .base import BaseRouter


class ModelAdminSerializer(ModelSerializer):
    class Meta:
        fields = []


class AdminRouter(BaseRouter):
    def register(self, model: Model, route: str, basename: str = ""):
        def inner(model_admin: ModelAdmin):
            site.register(model, model_admin)
            self._log(
                "Routing admin viewset "
                + str(model_admin)
                + " to "
                + self.endpoint
                + route
            )

            class _viewset(ModelViewSet):
                model_admin: ModelAdmin
                permission_classes = [IsAdminUser]
                filterset_fields = []
                search_fields = []

                def get_queryset(self):
                    return self.model_admin.get_queryset(self.request)

                def get_serializer_class(self):
                    cls = ModelAdminSerializer
                    cls.Meta.model = self.model_admin.model
                    cls.Meta.fields = self.model_admin.list_display
                    return cls

                @classmethod
                def from_admin(cls, model_admin: ModelAdmin):
                    cls.model_admin = model_admin
                    cls.filterset_fields = model_admin.list_filter
                    cls.search_fields = model_admin.search_fields

                    if hasattr(model_admin, "filter_backends"):
                        cls.filter_backends = getattr(model_admin, "filter_backends")

                    if hasattr(model_admin, "filterset_class"):
                        cls.filterset_class = getattr(model_admin, "filterset_class")

                    if hasattr(model_admin, "pagination_class"):
                        cls.pagination_class = getattr(model_admin, "pagination_class")

                    return cls

            _viewset = _viewset.from_admin(model_admin(model, site))
            self._router.register(route, _viewset, basename=basename or route)
            return _viewset

        return inner
