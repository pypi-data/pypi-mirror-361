from drf_decorator_router import TSRouter
from drf_decorator_router.admin_router import AdminRouter

router = TSRouter("api/v1/", "api-v1")

admin_router = AdminRouter("api/admin/", "admin-api")
