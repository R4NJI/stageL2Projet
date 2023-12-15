# Generated by Django 4.2.6 on 2023-11-19 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stagiaires', '0014_demande_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='stage',
            name='destinataire',
            field=models.CharField(blank=True, choices=[('DRH', 'DRH'), ('DSI', 'DSI'), ('DAF', 'DAF')], default='DRH', max_length=255, null=True),
        ),
    ]