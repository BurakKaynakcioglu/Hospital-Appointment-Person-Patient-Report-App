# Generated by Django 5.0.4 on 2024-05-07 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userpage', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='randevular',
            name='randevuSaati',
            field=models.CharField(max_length=5, null=True),
        ),
    ]
