# Generated by Django 4.2.6 on 2023-12-05 09:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stagiaires', '0023_alter_etudiant_rapport'),
    ]

    operations = [
        migrations.AlterField(
            model_name='etudiant',
            name='personnel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='etudiantPersonnel', to='stagiaires.personnel'),
        ),
    ]