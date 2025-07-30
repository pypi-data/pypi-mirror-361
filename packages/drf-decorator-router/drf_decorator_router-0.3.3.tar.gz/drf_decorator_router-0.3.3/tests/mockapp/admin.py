from django.contrib import admin

from drf_decorator_router.pagination import StandardResultsSetPagination

from . import models
from .routers import admin_router


@admin_router.register(models.MockProduct, "mock-product")
class MockProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "store")
    list_filter = ("store", "store__organization")
    search_fields = ("name",)
    pagination_class = StandardResultsSetPagination

@admin_router.register(models.MockStore, "mock-store")
class MockStoreAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "organization")
    search_fields = ("name",)
