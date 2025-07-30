from collections import namedtuple

from django.http import HttpResponse
from django.urls import path
from rest_framework.fields import Field
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import View
from rest_framework.viewsets import ViewSet

from drf_decorator_router.router import Router

NUMBER_FIELDS = ['IntegerField', 'FloatField', 'DecimalField']
STRING_FIELDS = ['CharField', 'TextField', 'SlugField', 'UUIDField', 'DateField', 'DateTimeField']
LIST_SERIALIZER = "ListSerializer"

INTERFACE_TEMPLATE = """
export interface {{name}}{
    {{fields}}
}
"""

BaseInterface = namedtuple("BaseInterface", ["name", "fields", "order"])


class BaseTranslator:
    interfaces: set[BaseInterface] = set()
    serializers: set[Serializer] = set()
    registered_serializers: set[str] = set()

    def get_interface_name(self, serializer: Serializer) -> str:
        return serializer.__class__.__name__.replace("Serializer", "")

    def get_interface_name_from_field(self, field: Field) -> str:
        return str(field).split("(")[0].replace("Serializer", "")

    def get_field_type(self, field: Field) -> str:
        name = field.__class__.__name__

        if name in NUMBER_FIELDS:
            return 'number'
        elif name in STRING_FIELDS:
            return 'string'
        elif name == LIST_SERIALIZER:
            return self.get_interface_name_from_field(field)

        return "unknown"

    def register_serializer(self, serializer: Serializer):
        name = self.get_interface_name(serializer)

        if name in self.registered_serializers:
            return

        fields = list(map(lambda f: f'{f[0]}: {self.get_field_type(f[1])}', serializer.get_fields().items()))
        self.registered_serializers.add(name)
        self.interfaces.add(BaseInterface(name, "\n".join(fields), 0))

    def interface_to_string(self, interface: BaseInterface) -> str:
        return INTERFACE_TEMPLATE.replace("{{name}}", interface.name).replace("{{fields}}", interface.fields)

    def register_view(self, view: View | ViewSet):
        view_instance = view()
        serializer = view_instance.get_serializer_class()()

        self.serializers.add(serializer)

    def get_typescript_file(self) -> str:
        for serializer in self.serializers:
            self.register_serializer(serializer)

        return "\n".join(map(lambda i: self.interface_to_string(i) ,self.interfaces))


class TSTypingsView(ListAPIView):
    translator: BaseTranslator

    def list(self, request, *args, **kwargs):
        return HttpResponse(
            self.translator.get_typescript_file(),
            content_type="text/javascript",
        )


class TSRouter(Router):
    translator = BaseTranslator()

    def process_viewset(self, viewset: ViewSet, route: str, basename: str) -> None:
        self.translator.register_view(viewset)

    def process_view(self, view: View, route: str, name: str) -> None:
        self.translator.register_view(view)

    def on_views_loaded(self) -> None:
        TSTypingsView.translator = self.translator

        self._urls.append(
            path("typings/", TSTypingsView.as_view(), name="django-ts-typings")
        )
