# Generated by Django 2.0.1 on 2018-01-29 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compare', '0008_auto_20180127_2242'),
    ]

    operations = [
        migrations.AddField(
            model_name='compare',
            name='submitted_url_compare_ready',
            field=models.BooleanField(default=False),
        ),
    ]
