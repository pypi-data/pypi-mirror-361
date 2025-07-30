from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from model_mommy import mommy

from .mockapp.models import MockProduct, MockStore


class DecoratorRouterAPITestCase(APITestCase):
    store_list_url = reverse("api-v1:mock-store-list")

    def setUp(self):
        self.store_1 = mommy.make(MockStore)
        self.store_2 = mommy.make(MockStore)

        for store in [self.store_1, self.store_2]:
            mommy.make(MockProduct, store=store, _quantity=10)

    def test_it_lists_stores_from_viewset(self):
        response = self.client.get(self.store_list_url)
        json = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json), 2)

    def test_it_retrieves_store_from_viewset(self):
        url = reverse("api-v1:mock-store-detail", (self.store_1.id,))
        response = self.client.get(url)
        json = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json['id'], self.store_1.id)