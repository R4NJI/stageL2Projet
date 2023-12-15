from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

#Modele pour la gestion des comptes
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('L\'adresse e-mail est requise')
        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
    
class Stage(models.Model):
    idStage = models.AutoField(primary_key=True)
    domaine = models.CharField(max_length=255)
    theme = models.CharField(max_length=255)
    niveau =  models.CharField(max_length=255,null=True,blank =True)
    ecole = models.TextField(null=True,blank =True)
    dateDebut = models.DateField()
    dateFin = models.DateField()
    statut = models.CharField(max_length=255, choices=(('En attente', 'En attente'), ('Accepté', 'Accepté'), ('Refusé', 'Refusé'), ('Terminé', 'Terminé'),('Expiré', 'Expiré')), default='En attente')
    destinataire =  models.CharField(max_length=255, choices=(('DRH','DRH'), ('DSI', 'DSI'), ('DAF', 'DAF')),default='DRH',null=True,blank =True)

class Rapport(models.Model):
    numeroRapport = models.AutoField(primary_key=True)
    rapportStage = models.FileField(upload_to='documents/')
    appreciation = models.FileField(upload_to='documents/',null=True)
    statutRapport = models.CharField(max_length=255, choices=(('En attente', 'En attente'), ('Validé', 'Validé'), ('Refusé', 'Refusé')),default='En attente')

class Personnel(models.Model):
    idPersonnel = models.AutoField(primary_key=True)
    im = models.CharField(max_length=255)
    nomPersonnel = models.CharField(max_length=255)
    prenomPersonnel = models.CharField(max_length=255)
    telephonePersonnel = models.CharField(max_length=255)
    emailPersonnel = models.EmailField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="personnelCompte",null=True, blank=True)


class Etudiant(models.Model):
    idEtudiant = models.AutoField(primary_key=True)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="etudiantStage",null=True, blank=True)
    rapport = models.ForeignKey(Rapport, on_delete=models.CASCADE, related_name="etudiantRapport", null=True, blank=True)
    personnel = models.ForeignKey(Personnel, on_delete=models.SET_NULL, related_name="etudiantPersonnel",null=True, blank=True)
    matricule = models.CharField(max_length=255)
    nomEtudiant = models.CharField(max_length=255)
    prenomEtudiant = models.CharField(max_length=255)
    adresseEtudiant = models.CharField(max_length=255)
    telephoneEtudiant = models.CharField(max_length=255)
    emailEtudiant = models.EmailField()

class Demande(models.Model):
    numeroDemande = models.AutoField(primary_key=True)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='demandes')
    cv = models.FileField(upload_to='documents/')
    lettreMotiv = models.FileField(upload_to='documents/')
    autreFichier = models.FileField(upload_to='documents/')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="demandeCompte",null=True, blank=True)

class Societe(models.Model):
    idSociete = models.AutoField(primary_key=True)
    sigle = models.CharField(max_length=255)
    telephoneSociete = models.CharField(max_length=255)
    emailSociete = models.EmailField()
    siteWeb = models.CharField(max_length=255, null=True)

