import django_filters
from .models import NetworkNode


class NetworkNodeFilter(django_filters.FilterSet):
    country = django_filters.CharFilter(
        field_name="contact__country", lookup_expr="icontains", label="Страна"
    )
    city = django_filters.CharFilter(
        field_name="contact__city", lookup_expr="icontains", label="Город"
    )
    product_name = django_filters.CharFilter(
        field_name="products__name", lookup_expr="icontains", label="Название продукта"
    )

    class Meta:
        model = NetworkNode
        fields = ["node_type", "level", "supplier", "country"]
