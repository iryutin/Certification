from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from .models import Contact, Product, NetworkNode


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["email", "country", "city", "street", "house_number"]
    list_filter = ["country", "city"]
    search_fields = ["email", "country", "city"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "model", "release_date"]
    list_filter = ["release_date"]
    search_fields = ["name", "model"]


def clear_debt(modeladmin, request, queryset):
    """Admin action для очистки задолженности"""
    updated_count = queryset.update(debt=0)
    modeladmin.message_user(
        request, f"Задолженность очищена у {updated_count} объектов"
    )


clear_debt.short_description = "Очистить задолженность перед поставщиком"


class CityFilter(admin.SimpleListFilter):
    """Фильтр по названию города"""

    title = "Город"
    parameter_name = "city"

    def lookups(self, request, model_admin):
        # Получаем уникальные города из контактов
        cities = Contact.objects.values_list("city", flat=True).distinct()
        return [(city, city) for city in cities if city]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(contact__city=self.value())
        return queryset


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "node_type",
        "level",
        "supplier_link",
        "debt",
        "created_at",
        "city",
    ]
    list_filter = ["node_type", "level", "created_at", CityFilter]
    search_fields = ["name", "contact__email"]
    list_editable = ["debt"]
    readonly_fields = ["created_at", "level", "supplier_link"]
    filter_horizontal = ["products"]
    actions = [clear_debt]

    def supplier_link(self, obj):
        """Ссылка на поставщика"""
        if obj.supplier:
            url = reverse(
                "admin:electronics_networknode_change", args=[obj.supplier.id]
            )
            return format_html('<a href="{}">{}</a>', url, obj.supplier.name)
        return "—"

    supplier_link.short_description = "Поставщик"

    def city(self, obj):
        """Город для отображения в списке"""
        return obj.contact.city if obj.contact else "—"

    city.short_description = "Город"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("supplier", "contact")
            .prefetch_related("products")
        )

    fieldsets = (
        (
            None,
            {"fields": ("name", "node_type", "contact", "supplier", "supplier_link")},
        ),
        ("Продукты", {"fields": ("products",)}),
        ("Финансы", {"fields": ("debt",)}),
        (
            "Системная информация",
            {"fields": ("level", "created_at"), "classes": ("collapse",)},
        ),
    )
