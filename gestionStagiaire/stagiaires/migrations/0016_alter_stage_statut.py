# Generated by Django 4.2.6 on 2023-11-25 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stagiaires', '0015_stage_destinataire'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stage',
            name='statut',
            field=models.CharField(choices=[('En attente', 'En attente'), ('Accepté', 'Accepté'), ('Refusé', 'Refusé'), ('Terminé', 'Terminé'), ('Expiré', 'Expiré')], default='En attente', max_length=255),
        ),
    ]
