from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .apps import WebConfig
from .views import NetworkNodeViewSet, ProductViewSet, ContactViewSet

app_name = WebConfig.name

router = DefaultRouter()
router.register(r"network-nodes", NetworkNodeViewSet)
router.register(r"products", ProductViewSet)
router.register(r"contacts", ContactViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
