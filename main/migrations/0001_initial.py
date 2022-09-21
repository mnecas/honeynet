# Generated by Django 4.0.6 on 2022-09-11 18:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Attacker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("source_addr", models.GenericIPAddressField()),
                ("source_port", models.IntegerField()),
                ("mac", models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name="Honeypot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                ("type", models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name="HoneypotHasAttacker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("data", models.JSONField()),
                ("timestamp", models.DateTimeField()),
                (
                    "attacker",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="main.attacker"
                    ),
                ),
                (
                    "honeypot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="main.honeypot"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AttackDump",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("path", models.CharField(max_length=64)),
                (
                    "honeypot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="main.honeypot"
                    ),
                ),
            ],
        ),
    ]
