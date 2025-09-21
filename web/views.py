from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from .models import NetworkNode, Product, Contact
from .serializers import NetworkNodeSerializer, ProductSerializer, ContactSerializer
from .filters import NetworkNodeFilter


class IsActiveUserPermission(permissions.BasePermission):
    """Права доступа только для активных пользователей"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active


class NetworkNodeViewSet(viewsets.ModelViewSet):
    queryset = (
        NetworkNode.objects.all()
        .select_related("contact", "supplier")
        .prefetch_related("products")
    )
    serializer_class = NetworkNodeSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = NetworkNodeFilter
    search_fields = ["name", "contact__country", "contact__city"]
    ordering_fields = ["created_at", "debt", "level"]
    ordering = ["-created_at"]
    permission_classes = [IsActiveUserPermission]

    def get_queryset(self):
        """Фильтрация по стране через query parameter"""
        queryset = super().get_queryset()
        country = self.request.query_params.get("country")
        if country:
            queryset = queryset.filter(contact__country__icontains=country)
        return queryset


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "model"]
    permission_classes = [IsActiveUserPermission]


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["country", "city", "email"]
    permission_classes = [IsActiveUserPermission]
