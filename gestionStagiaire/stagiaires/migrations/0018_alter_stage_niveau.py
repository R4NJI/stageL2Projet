# Generated by Django 4.2.6 on 2023-11-29 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stagiaires', '0017_stage_niveau'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stage',
            name='niveau',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
