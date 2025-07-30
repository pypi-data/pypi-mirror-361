from django.urls import path
from rest_framework.views import View
from rest_framework.viewsets import ViewSet

from drf_decorator_router.base import BaseRouter


class Router(BaseRouter):
    def process_viewset(self, viewset: ViewSet, route: str, basename: str) -> None:
        pass

    def process_view(self, view: View, route: str, name: str) -> None:
        pass

    def route_viewset(self, route: str, basename: str = ""):
        def inner(viewset):
            self._log(
                "Routing viewset " + str(viewset) + " to " + self.endpoint + route
            )
            self.process_viewset(viewset, route, basename)
            self._router.register(route, viewset, basename=basename)
            return viewset

        return inner

    def route_view(self, route: str, name: str = ""):
        def inner(view):
            self._log("Routing view " + str(view) + " to " + self.endpoint + route)
            self.process_view(view, route, name)
            self._urls.append(path(route, view.as_view(), name=name))
            return view

        return inner
