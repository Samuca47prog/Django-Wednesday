# Generated by Django 4.1 on 2023-02-16 00:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="venue",
            name="email_address",
            field=models.EmailField(
                blank=True, max_length=254, verbose_name="Email Address"
            ),
        ),
        migrations.AlterField(
            model_name="venue",
            name="phone",
            field=models.CharField(
                blank=True, max_length=15, verbose_name="Contact phone"
            ),
        ),
        migrations.AlterField(
            model_name="venue",
            name="web",
            field=models.URLField(blank=True, verbose_name="Website Address"),
        ),
    ]
