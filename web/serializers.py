from rest_framework import serializers
from .models import Contact, Product, NetworkNode


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class NetworkNodeSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    products = ProductSerializer(many=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    level = serializers.IntegerField(read_only=True)
    country = serializers.CharField(source="contact.country", read_only=True)

    class Meta:
        model = NetworkNode
        fields = [
            "id",
            "name",
            "node_type",
            "contact",
            "products",
            "supplier",
            "supplier_name",
            "debt",
            "created_at",
            "level",
            "country",
        ]
        read_only_fields = ["created_at", "level", "debt"]  # Запрещаем обновление debt

    def create(self, validated_data):
        contact_data = validated_data.pop("contact")
        products_data = validated_data.pop("products")

        contact = Contact.objects.create(**contact_data)
        node = NetworkNode.objects.create(contact=contact, **validated_data)

        for product_data in products_data:
            product, created = Product.objects.get_or_create(**product_data)
            node.products.add(product)

        return node

    def update(self, instance, validated_data):
        # Удаляем debt из validated_data, если он присутствует
        validated_data.pop("debt", None)

        contact_data = validated_data.pop("contact", None)
        products_data = validated_data.pop("products", None)

        # Обновление контактов
        if contact_data:
            contact_serializer = ContactSerializer(
                instance.contact, data=contact_data, partial=True
            )
            if contact_serializer.is_valid():
                contact_serializer.save()

        # Обновление продуктов
        if products_data is not None:
            instance.products.clear()
            for product_data in products_data:
                product, created = Product.objects.get_or_create(**product_data)
                instance.products.add(product)

        # Обновление остальных полей
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
