Decorator Router for Django Rest Framework
==========================================

[![build](https://github.com/brenodega28/drf-decorator-router/actions/workflows/build.yml/badge.svg)](https://github.com/brenodega28/drf-decorator-router/actions/workflows/build.yml)

About
-----
Django Rest Framework package to quickly route your views with decorators.
Very lightweight and simple code using only Django and Rest Framework as dependencies.

Supported Versions
------------------
* Python 3.6 and above
* Django >= 2.2
* Django REST Framework >=3.7.0

Installation
------------
```shell
pip install drf-decorator-router
```

How to Use
----------

#### main_app/routes.py
```python
from rest_framework import generics, viewsets
from drf_decorator_router import Router

# Declaring the router
router = Router("api/v1", namespace="api-v1")
```

#### example_app/views.py
```python
@router.route_view("login/", "user-login") # /api/v1/login/
class LoginView(generics.CreateAPIView):
    pass

@router.route_view("company/<int:company_id>/login/", "company-user-login") # /api/v1/company/10/login/
class LoginForCompanyView(generics.CreateAPIView):
    pass

@router.route_viewset("users", "users") # /api/v1/users/
class UserViewSet(viewsets.ModelViewSet):
    pass
```
<b>Important:</b> The decorated view/viewset <u>must be declared or imported</u> in the `views.py` file, or else it
won't be routed. You can also change the file name from which the views will be loaded by adding a `AUTO_ROUTER_MODULES`
in settings.py. Example: `AUTO_ROUTER_MODULES=['decorated_views', 'views']`.

#### main_app/urls.py
```python
from main_app.routers import router

urlpatterns = [
    router.path
]
```

#### Reversing
```python
from rest_framework.reverse import reverse

login_view = reverse("api-v1:user-login")
user_list = reverse("api-v1:users-list")
user_detail = reverse("api-v1:users-detail", (10,))
```
