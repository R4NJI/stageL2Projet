# Generated by Django 4.2.6 on 2023-10-28 15:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Personnel',
            fields=[
                ('im', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('telephonePersonnel', models.CharField(max_length=255)),
                ('emailPersonnel', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Societe',
            fields=[
                ('idSociete', models.AutoField(primary_key=True, serialize=False)),
                ('sigle', models.CharField(max_length=255)),
                ('telephoneSociete', models.CharField(max_length=255)),
                ('emailSociete', models.EmailField(max_length=254)),
                ('siteWeb', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Stage',
            fields=[
                ('idStage', models.AutoField(primary_key=True, serialize=False)),
                ('domaine', models.CharField(max_length=255)),
                ('theme', models.CharField(max_length=255)),
                ('dateDebut', models.DateField()),
                ('dateFin', models.DateField()),
                ('statut', models.CharField(choices=[('En attente', 'En attente'), ('Accepté', 'Accepté'), ('Refusé', 'Refusé'), ('Terminé', 'Terminé')], max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Etudiant',
            fields=[
                ('idEtudiant', models.AutoField(primary_key=True, serialize=False)),
                ('matricule', models.CharField(max_length=255)),
                ('nomEtudiant', models.CharField(max_length=255)),
                ('prenomEtudiant', models.CharField(max_length=255)),
                ('adresseEtudiant', models.CharField(max_length=255)),
                ('ecole', models.TextField()),
                ('filiere', models.CharField(max_length=255)),
                ('emailEtudiant', models.EmailField(max_length=254)),
                ('stage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='etudiants', to='stagiaires.stage')),
            ],
        ),
        migrations.CreateModel(
            name='Demande',
            fields=[
                ('numeroDemande', models.AutoField(primary_key=True, serialize=False)),
                ('cv', models.FileField(upload_to='documents/')),
                ('lettreMotiv', models.FileField(upload_to='documents/')),
                ('autreFichier', models.FileField(upload_to='documents/')),
                ('etudiant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='demandes', to='stagiaires.etudiant')),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=30, unique=True)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
