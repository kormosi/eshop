from decimal import Decimal

from django.db import migrations


def create_shipping_product(apps, schema_editor):
    Product = apps.get_model("eshop", "Product")
    Product.objects.create(
        name="Doprava",
        description="Flat delivery fee.",
        price=Decimal("2.70"),
        currency="EUR",
        vat_rate=Decimal("23.00"),
        active=True,
        is_shipping=True,
    )


def delete_shipping_product(apps, schema_editor):
    Product = apps.get_model("eshop", "Product")
    Product.objects.filter(is_shipping=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("eshop", "0009_product_is_shipping"),
    ]

    operations = [
        migrations.RunPython(create_shipping_product, delete_shipping_product),
    ]
