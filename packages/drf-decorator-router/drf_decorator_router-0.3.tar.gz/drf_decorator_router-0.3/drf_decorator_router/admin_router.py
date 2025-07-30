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

            class ModelAdminViewSet(ModelViewSet):
                model_admin: ModelAdmin
                permission_classes = [IsAdminUser]

                def get_queryset(self):
                    return self.model_admin.get_queryset(self.request)

                def get_serializer_class(self):
                    cls = ModelAdminSerializer
                    cls.Meta.model = self.model_admin.model
                    cls.Meta.fields = self.model_admin.list_display

                    print(dir(self.model_admin.get_changelist_form(self.request)))
                    print(
                        self.model_admin.get_changelist_form(self.request).base_fields
                    )

                    return cls

            viewset = ModelAdminViewSet
            viewset.model_admin = model_admin(model, site)
            self._router.register(route, viewset, basename=basename)
            return viewset

        return inner
