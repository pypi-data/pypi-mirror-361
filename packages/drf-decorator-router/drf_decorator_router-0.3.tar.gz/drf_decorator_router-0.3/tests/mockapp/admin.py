from django.contrib import admin

from . import models
from .routers import admin_router


@admin_router.register(models.MockProduct, "mock-product")
class MockProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "store")


@admin_router.register(models.MockStore, "mock-store")
class MockStoreAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
