# Generated by Django 5.0.4 on 2024-05-06 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpage', '0011_alter_raporlar_hastaid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resimler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images/')),
            ],
        ),
    ]
