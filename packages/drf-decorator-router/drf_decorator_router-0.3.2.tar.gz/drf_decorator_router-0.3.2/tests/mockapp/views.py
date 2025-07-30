from rest_framework import viewsets, generics
from rest_framework.response import Response

from .routers import router

from . import models, serializers


@router.route_viewset("mock-store", "mock-store")
class MockStoreViewSet(viewsets.ModelViewSet):
    queryset = models.MockStore.objects.all()
    serializer_class = serializers.MockStoreSerializer


@router.route_view("mock-products/", "mock-products")
class MockProductsListView(generics.ListAPIView):
    queryset = models.MockProduct.objects.all()
    serializer_class = serializers.MockProductSerializer


@router.route_view("mock-store/<int:store_id>/mock-products/", "mock-store-products")
class MockStoreProductsListView(MockProductsListView):
    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(store__id=kwargs.get('store_id'))
        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data)
