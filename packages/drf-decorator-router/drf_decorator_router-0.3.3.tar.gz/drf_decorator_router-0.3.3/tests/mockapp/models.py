from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MockStore(TimeStampedModel):
    organization = models.CharField(max_length=50)
    name = models.CharField(max_length=30)

    def __str__(self) -> str:
        return self.name


class MockProduct(TimeStampedModel):
    name = models.CharField(max_length=30)
    store = models.ForeignKey(MockStore, on_delete=models.CASCADE)
    product_code = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"({self.store.name}) - {self.name}"

    @property
    def organization(self):
        return self.store.organization
