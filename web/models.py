from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Contact(models.Model):
    email = models.EmailField(verbose_name='Email')
    country = models.CharField(max_length=100, verbose_name='Страна')
    city = models.CharField(max_length=100, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house_number = models.CharField(max_length=10, verbose_name='Номер дома')

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return f'{self.country}, {self.city}, {self.street}, {self.house_number}'


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    model = models.CharField(max_length=100, verbose_name='Модель')
    release_date = models.DateField(verbose_name='Дата выхода на рынок')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return f'{self.name} {self.model}'


class NetworkNode(models.Model):
    NODE_TYPES = (
        ('factory', 'Завод'),
        ('retail', 'Розничная сеть'),
        ('entrepreneur', 'Индивидуальный предприниматель'),
    )

    name = models.CharField(max_length=100, verbose_name='Название')
    node_type = models.CharField(
        max_length=20,
        choices=NODE_TYPES,
        verbose_name='Тип звена'
    )
    contact = models.OneToOneField(
        Contact,
        on_delete=models.CASCADE,
        verbose_name='Контакты'
    )
    products = models.ManyToManyField(
        Product,
        verbose_name='Продукты'
    )
    supplier = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Поставщик'
    )
    debt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Задолженность перед поставщиком'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время создания'
    )
    level = models.IntegerField(
        default=0,
        editable=False,
        verbose_name='Уровень иерархии'
    )

    class Meta:
        verbose_name = 'Звено сети'
        verbose_name_plural = 'Звенья сети'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_node_type_display()}: {self.name}'

    def save(self, *args, **kwargs):
        # Автоматическое определение уровня иерархии
        if self.supplier:
            self.level = self.supplier.level + 1
        else:
            self.level = 0  # Завод всегда уровень 0

        # Проверка, что завод не может иметь поставщика
        if self.node_type == 'factory' and self.supplier:
            raise ValueError("Завод не может иметь поставщика")

        super().save(*args, **kwargs)
