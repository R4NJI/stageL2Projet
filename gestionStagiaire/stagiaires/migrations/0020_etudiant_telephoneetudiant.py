# Generated by Django 4.2.6 on 2023-12-04 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stagiaires', '0019_personnel_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='etudiant',
            name='telephoneEtudiant',
            field=models.CharField(default='0000', max_length=255),
        ),
    ]