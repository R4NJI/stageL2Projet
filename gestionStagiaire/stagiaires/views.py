from datetime import date
import os
from django.conf import settings
from django.contrib.auth import authenticate,login,logout,get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse,HttpResponseRedirect, JsonResponse
from django.template import loader
from .models import Etudiant,Stage,CustomUser,Demande,Rapport,Personnel
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from django.contrib import messages
from .signals import stage_date_expired
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
from urllib.parse import quote
from django.utils.text import get_valid_filename
from django.db.models import Q
from dateutil.relativedelta import relativedelta

#Pour l'authentification
def check_superuser(request):
    return request.user.is_authenticated and request.user.is_superuser


# Create your views here.
def index(request):
    etudiant=Etudiant.objects.all().values()
    template=loader.get_template("index.html")
    context = {
        'stagiaires': etudiant
    }
    return HttpResponse(template.render(context,request))

def navbar(request):
    # Récupérez l'information de la session
    load_rapport = request.session.pop('load_rapport', False)
    load_demande = request.session.pop('load_demande', False)
    load_personnel = request.session.pop('load_personnel', False)

    # Vérifiez si l'utilisateur est connecté et est un superutilisateur
    is_superuser = check_superuser(request)

    # récupérer l'username de l'utilisateur
    username = request.user.username if request.user.is_authenticated else None

    context = {
        'is_superuser': is_superuser,
        'load_rapport': load_rapport,
        'load_demande': load_demande,
        'load_personnel': load_personnel,
        'username': username
    }

    if username:
        return render(request, 'navbar.html', context)
    else:
        return render(request,'404.html')

def statistique(request):
    # Vérifiez d'abord les dates de fin des stages expirés
    check_expired_stages(None)

    stages_attente = Stage.objects.filter(statut="En attente")
    stages_accepte = Stage.objects.filter(statut="Accepté")
    stages_refuse = Stage.objects.filter(statut="Refusé")
    stages_termine = Stage.objects.filter(statut="Terminé")
    stages_expire = Stage.objects.filter(statut="Expiré")
    stages = Stage.objects.all()


    rapport_attente = Rapport.objects.filter(statutRapport="En attente")
    rapport_valide = Rapport.objects.filter(statutRapport="Validé")
    rapport_refuse = Rapport.objects.filter(statutRapport="Refusé")
    rapports = Rapport.objects.all()
    

    # Comptez le nombre de stages 
    nombre_stages_attente = stages_attente.count()
    nombre_stages_accepte = stages_accepte.count()
    nombre_stages_refuse = stages_refuse.count()
    nombre_stages_termine = stages_termine.count()
    nombre_stages_expire = stages_expire.count()
    nombre_stages = stages.count()


    # Comptez le nombre de stages
    nombre_rapport_attente = rapport_attente.count()
    nombre_rapport_valide = rapport_valide.count()
    nombre_rapport_refuse = rapport_refuse.count()
    nombre_rapport = rapports.count()

    # Utilisez cette variable dans votre contexte ou où vous en avez besoin
    context = {
        'nombre_stages_attente': nombre_stages_attente,
        'nombre_stages_accepte': nombre_stages_accepte,
        'nombre_stages_refuse': nombre_stages_refuse,
        'nombre_stages_termine': nombre_stages_termine,
        'nombre_stages_expire': nombre_stages_expire,
        'total': nombre_stages,
        'nombre_rapport_attente' : nombre_rapport_attente,
        'nombre_rapport_valide' : nombre_rapport_valide,
        'nombre_rapport_refuse' : nombre_rapport_refuse,
        'totalRapport': nombre_rapport
    }

    return render(request, 'statis.html', context)

def faire_demande(request):
    
    context = {
        'stagiaires': 'Faire une demande'
    }
    return render(request, 'faire_demande.html', context)

def monome(request):
    
    context = {
        'ismonome' : True
    }
    return render(request, 'faire_demande.html', context)

def binome(request):
    
    context = {
        'ismonome' : False
    }
    return render(request, 'faire_demande.html', context)

def check_expired_stages(request):
    stage_date_expired.send(sender=Stage)

def demande(request):

    user_id = request.user.id if request.user.is_authenticated else None

    demandes = Demande.objects.filter(etudiant__stage__statut="En attente")

    # Utilisation de la fonction dans votre vue
    is_superuser = check_superuser(request)

    context = {
        'is_superuser': is_superuser,
        'demandes':demandes,
        'type':'En attente',
        'user_id': user_id
    }

    return render(request, 'demande.html', context)

def demande_acceptee(request):
    # Vérifiez d'abord les dates de fin des stages expirés
    check_expired_stages(None)

    demandes = Demande.objects.filter(etudiant__stage__statut="Accepté")
    
    # Utilisation de la fonction dans votre vue
    is_superuser = check_superuser(request)
    
    context = {
        'is_superuser': is_superuser,
        'demandes': demandes,
        'type':'Accepté'
    }
    return render(request, 'demande.html', context)

def demande_refusee(request):

    demandes = Demande.objects.filter(etudiant__stage__statut="Refusé")
        
    # Utilisation de la fonction dans votre vue
    is_superuser = check_superuser(request)

    context = {
        'is_superuser': is_superuser,
        'demandes': demandes,
        'type':'Refusé'
    }
    return render(request, 'demande.html', context)

def demande_modifiee(request,idEtudiant):
    demande = Demande.objects.get(etudiant__idEtudiant=idEtudiant)
    context = {
        'demande': demande
    }
    return render(request, 'demande_modifiee.html', context)

def modifier_demande(request,idEtudiant):
    demande = Demande.objects.get(etudiant__idEtudiant=idEtudiant)
    if request.method == 'POST':
 
        matricule = request.POST.get('matricule')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        adresse = request.POST.get('adresse')
        ecole = request.POST.get('ecole')
        domaine = request.POST.get('domaine')
        theme = request.POST.get('theme')
        dateDebut = request.POST.get('dateDebut')
        dateFin = request.POST.get('dateFin')
        destinataire = request.POST.get('destinataire')
        telephone = request.POST.get('tel')
        email = request.POST.get('email')
        
        # Utilisez request.FILES pour les fichiers
        cv = request.FILES.get('cv') 
        lettreMotiv = request.FILES.get('lettreMotiv')  
        autreFichier = request.FILES.get('autreFichier')  

        # Enregistrez les fichiers dans le répertoire "media/documents"
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'documents'))
        
        # Récupérez les extensions des fichiers
        # Génération des noms de fichiers uniques
        # Enregistrez les fichiers avec les noms uniques
        # Modification d'une instance de Demande
        if cv:
            cv_ext= os.path.splitext(cv.name)[1]
            cv_filename = get_valid_filename(f"{matricule}_{nom}_cv{cv_ext}")
            cv_path = fs.save(cv_filename, cv)
            demande.cv = cv_path

        if lettreMotiv:
            lettreMotiv_ext= os.path.splitext(lettreMotiv.name)[1]
            lettreMotiv_filename = get_valid_filename(f"{matricule}_{nom}_lm{lettreMotiv_ext}")
            lettreMotiv_path = fs.save(lettreMotiv_filename, lettreMotiv)
            demande.lettreMotiv = lettreMotiv_path

        if autreFichier:
            autreFichier_ext= os.path.splitext(autreFichier.name)[1]
            autreFichier_filename = get_valid_filename(f"{matricule}_{nom}_autre{autreFichier_ext}")
            autreFichier_path = fs.save(autreFichier_filename, autreFichier)
            demande.autreFichier = autreFichier_path
    

        # Modification d'une instance de Stage
        demande.etudiant.stage.domaine=domaine
        demande.etudiant.stage.theme=theme
        demande.etudiant.stage.ecole=ecole
        demande.etudiant.stage.dateDebut=dateDebut
        demande.etudiant.stage.dateFin=dateFin
        demande.etudiant.stage.destinataire=destinataire
        demande.etudiant.stage.save()

        # Modification d'une instance d'Étudiant associée au stage
        
        demande.etudiant.matricule=matricule 
        demande.etudiant.nomEtudiant=nom
        demande.etudiant.prenomEtudiant=prenom
        demande.etudiant.adresseEtudiant=adresse
        demande.etudiant.telephoneEtudiant=telephone
        demande.etudiant.emailEtudiant=email
        demande.etudiant.save()

  
        demande.save()

        messages.success(request, 'La demande a été modifiée avec succès.')

        # Stockez l'information dans la session
        request.session['load_demande'] = True

        return HttpResponseRedirect(reverse('navbar'))


def stage_termine(request):

    demandes = Demande.objects.filter(etudiant__stage__statut="Terminé")

    # Utilisation de la fonction dans votre vue
    is_superuser = check_superuser(request)

    context = {
        'is_superuser': is_superuser,
        'demandes': demandes,
        'type':'Terminé'
    }
    return render(request, 'demande.html', context)

def stage_expire(request):
    # Vérifiez d'abord les dates de fin des stages expirés
    check_expired_stages(None)
    
    demandes = Demande.objects.filter(etudiant__stage__statut="Expiré")

    # Utilisation de la fonction dans votre vue
    is_superuser = check_superuser(request)

    context = {
        'is_superuser': is_superuser,
        'demandes': demandes,
        'type':'Expiré'
    }
    return render(request, 'demande.html', context)

#quand on appuie sur le bouton rechercher de demande

def demande_search(request):
    param = request.GET.get("param")
    typevar = request.GET.get("type")
  
    user_id = request.user.id if request.user.is_authenticated else None
          
    if param and typevar:
        # Initialisez le filtre avec une condition vide
        filter_condition = Q()
        # Vérifiez si le paramètre est un nombre (idEtudiant)
        if param.isdigit():
            filter_condition |= Q(etudiant__matricule=param)
        else:
            # Le paramètre n'est pas un nombre, donc filtre par nom ou prénom
            filter_condition |= Q(etudiant__nomEtudiant__icontains=param) | Q(etudiant__prenomEtudiant__icontains=param) | Q(etudiant__stage__theme__icontains=param)

        demandes = Demande.objects.filter(
            filter_condition,
            etudiant__stage__statut=typevar
        )
    else:
        demandes = Demande.objects.filter(etudiant__stage__statut=typevar)

    # Utilisation de la fonction dans votre vue
    is_superuser = check_superuser(request)

    context = {
        'is_superuser': is_superuser,
        'demandes': demandes,
        'type' : typevar,
        'user_id' : user_id
    }

    return render(request, 'demande.html', context)

def demande_filtreDSI(request):
    typevar = request.GET.get("type")
  
    user_id = request.user.id if request.user.is_authenticated else None      

    if typevar:
        demandes = Demande.objects.filter(
            etudiant__stage__destinataire = "DSI",
            etudiant__stage__statut=typevar
        )
    else:
        demandes = Demande.objects.filter(etudiant__stage__statut=typevar)

    # Utilisation de la fonction dans votre vue
    is_superuser = check_superuser(request)

    context = {
        'is_superuser': is_superuser,
        'demandes': demandes,
        'type' : typevar,
        'user_id' : user_id
    }

    return render(request, 'demande.html', context)

def demande_filtreDRH(request):
    typevar = request.GET.get("type")
  
    user_id = request.user.id if request.user.is_authenticated else None

    if typevar:
        demandes = Demande.objects.filter(
            etudiant__stage__destinataire = "DRH",
            etudiant__stage__statut=typevar
        )
    else:
        demandes = Demande.objects.filter(etudiant__stage__statut=typevar)

    # Utilisation de la fonction dans votre vue
    is_superuser = check_superuser(request)

    context = {
        'is_superuser': is_superuser,
        'demandes': demandes,
        'type' : typevar,
        'user_id' : user_id
    }

    return render(request, 'demande.html', context)

def demande_filtreDAF(request):
    typevar = request.GET.get("type")
  
    user_id = request.user.id if request.user.is_authenticated else None
          
    if typevar:
        demandes = Demande.objects.filter(
            etudiant__stage__destinataire = "DAF",
            etudiant__stage__statut=typevar
        )
    else:
        demandes = Demande.objects.filter(etudiant__stage__statut=typevar)

    # Utilisation de la fonction dans votre vue
    is_superuser = check_superuser(request)

    context = {
        'is_superuser': is_superuser,
        'demandes': demandes,
        'type' : typevar,
        'user_id' : user_id
    }

    return render(request, 'demande.html', context)


def rapport(request):
    # récupérer l'id de l'utilisateur
    user_id = request.user.id if request.user.is_authenticated else None
    # Utilisation de la fonction dans votre vue
    is_superuser = check_superuser(request)

    if is_superuser:
        demandes = Demande.objects.filter(Q(etudiant__stage__statut="Accepté") | Q(etudiant__stage__statut="Terminé"),etudiant__personnel__user__id=user_id)
    else :
        demandes = Demande.objects.filter(Q(etudiant__stage__statut="Accepté") | Q(etudiant__stage__statut="Terminé"))

    context = {
        'demandes': demandes,
        'is_superuser': is_superuser,
        'type': 'Tout',
        'user_id': user_id
    }
    return render(request,'rapport.html',context)

def rapport_search(request):
    # récupérer l'id de l'utilisateur
    user_id = request.user.id if request.user.is_authenticated else None

    param = request.GET.get("param")
    typevar = request.GET.get("type")
    
    # Utilisation de la fonction dans votre vue
    is_superuser = check_superuser(request)

    if param and typevar:
        # Initialisez le filtre avec une condition vide
        filter_condition = Q()
        # Vérifiez si le paramètre est un nombre (idEtudiant)
        if param.isdigit():
            filter_condition |= Q(etudiant__matricule=param)
        else:
            # Le paramètre n'est pas un nombre, donc filtre par nom ou prénom
            filter_condition |= Q(etudiant__nomEtudiant__icontains=param) | Q(etudiant__prenomEtudiant__icontains=param) | Q(etudiant__stage__theme__icontains=param)
        
        if typevar != "Tout":
            if is_superuser:
                demandes = Demande.objects.filter(
                    filter_condition,
                    etudiant__rapport__statutRapport=typevar,
                    etudiant__personnel__user__id=user_id
                )
            else:
                demandes = Demande.objects.filter(
                    filter_condition,
                    etudiant__rapport__statutRapport=typevar
                )
        else:
            if is_superuser:
                demandes = Demande.objects.filter(
                    filter_condition,
                    etudiant__personnel__user__id=user_id
                )
            else:
                demandes = Demande.objects.filter(
                    filter_condition
                )
                
           
    else:
        if typevar == "Tout":
            if is_superuser:
                demandes = Demande.objects.filter(Q(etudiant__stage__statut="Accepté") | Q(etudiant__stage__statut="Terminé"),etudiant__personnel__user__id=user_id)
            else:
                demandes = Demande.objects.filter(Q(etudiant__stage__statut="Accepté") | Q(etudiant__stage__statut="Terminé"))
        else:
            if is_superuser: 
                demandes = Demande.objects.filter(Q(etudiant__stage__statut="Accepté") | Q(etudiant__stage__statut="Terminé"),etudiant__rapport__statutRapport=typevar,etudiant__personnel__user__id=user_id)
            else:
                demandes = Demande.objects.filter(Q(etudiant__stage__statut="Accepté") | Q(etudiant__stage__statut="Terminé"),etudiant__rapport__statutRapport=typevar)


    context = {
        'demandes':demandes,
        'is_superuser': is_superuser,
        'type' : typevar,
        'user_id': user_id
    }

    return render(request, 'rapport.html', context)

def rapportAttente(request):
    # récupérer l'id de l'utilisateur
    user_id = request.user.id if request.user.is_authenticated else None

     # Utilisation de la fonction dans votre vue
    is_superuser = check_superuser(request)

    if is_superuser:
        demandes = Demande.objects.filter(Q(etudiant__stage__statut="Accepté") | Q(etudiant__stage__statut="Terminé"),etudiant__rapport__statutRapport="En attente",etudiant__personnel__user__id=user_id)
    else :
        demandes = Demande.objects.filter(Q(etudiant__stage__statut="Accepté") | Q(etudiant__stage__statut="Terminé"),etudiant__rapport__statutRapport="En attente")
    
    
    
    context = {
        'is_superuser': is_superuser,
        'demandes': demandes,
        'type': 'En attente',
        'user_id': user_id
    }
    return render(request,'rapport.html',context)

def rapportValide(request):
    # récupérer l'id de l'utilisateur
    user_id = request.user.id if request.user.is_authenticated else None

    # Utilisation de la fonction dans votre vue
    is_superuser = check_superuser(request)

    if is_superuser:
        demandes = Demande.objects.filter(Q(etudiant__stage__statut="Accepté") | Q(etudiant__stage__statut="Terminé"),etudiant__rapport__statutRapport="Validé",etudiant__personnel__user__id=user_id)
    else :
        demandes = Demande.objects.filter(Q(etudiant__stage__statut="Accepté") | Q(etudiant__stage__statut="Terminé"),etudiant__rapport__statutRapport="Validé")
    
    context = {
        'is_superuser': is_superuser,
        'demandes': demandes,
        'type': 'Validé',
        'user_id': user_id
    }
    return render(request,'rapport.html',context)

def rapportRefuse(request):
    # récupérer l'id de l'utilisateur
    user_id = request.user.id if request.user.is_authenticated else None

    # Utilisation de la fonction dans votre vue
    is_superuser = check_superuser(request)

    if is_superuser:
        demandes = Demande.objects.filter(Q(etudiant__stage__statut="Accepté") | Q(etudiant__stage__statut="Terminé"),etudiant__rapport__statutRapport="Refusé",etudiant__personnel__user__id=user_id)
    else :
        demandes = Demande.objects.filter(Q(etudiant__stage__statut="Accepté") | Q(etudiant__stage__statut="Terminé"),etudiant__rapport__statutRapport="Refusé")
    context = {
        'is_superuser': is_superuser,
        'demandes': demandes,
        'type': 'Refusé',
        'user_id': user_id
    }

    return render(request,'rapport.html',context)

def faire_rapport(request):
    # Utilisation de la fonction dans votre vue
    is_superuser = check_superuser(request)
    context = {
        'is_superuser': is_superuser,
    }
    return render(request,'faire_rapport.html',context)

def ajouter_rapport(request,idEtudiant):
    if request.method == 'POST':

        rapportStage = request.FILES.get('rapportStage')

        # Récupérez l'étudiant
        etudiant = Etudiant.objects.get(idEtudiant=idEtudiant)
        etudiants = Etudiant.objects.filter(stage__idStage=etudiant.stage.idStage)

        # Enregistrez les fichiers dans le répertoire "media/documents"
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'documents'))

        # Récupérez l'extension du fichier
        rapportStage_ext = os.path.splitext(rapportStage.name)[1]

        # Génération du nom du fichier unique
        rapportStage_filename = get_valid_filename(f"{idEtudiant}_rapportStage{rapportStage_ext}")

        #Enregistrez le fichier avec le nom unique
        rapportStage_path = fs.save(rapportStage_filename, rapportStage)

        if not etudiant.rapport:
            # Créez un rapport
            rapport = Rapport(rapportStage=rapportStage_path)
            for x in etudiants:
                # Associez le rapport à l'étudiant
                x.rapport = rapport
                x.rapport.statutRapport = "En attente"

                # Sauvegardez le rapport dans la base de données
                rapport.save()

                # Sauvegardez également l'étudiant pour mettre à jour la relation
                x.save()

        else:
            for x in etudiants:
                # Associez le rapport à l'étudiant
                x.rapport.rapportStage = rapportStage_path
                x.rapport.statutRapport = "En attente"

                # Sauvegardez le rapport dans la base de données
                x.rapport.save()

                # Sauvegardez également l'étudiant pour mettre à jour la relation
                x.save()

        # Renvoyez un message de confirmation
        messages.success(request, 'Le rapport de stage a été envoyé avec succès.')


        is_superuser = check_superuser(request)

        # Stockez l'information dans la session
        request.session['load_rapport'] = True

        # Redirigez vers la vue navbar
        return HttpResponseRedirect(reverse('navbar'))
    
def ajouter_appreciation(request,idEtudiant):
    if request.method == 'POST':
    
        appreciation = request.FILES.get('appreciation')

        # Récupérez l'étudiant
        etudiant = Etudiant.objects.get(idEtudiant=idEtudiant)
        etudiants = Etudiant.objects.filter(stage__idStage=etudiant.stage.idStage)

        # Enregistrez les fichiers dans le répertoire "media/documents"
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'documents'))

        # Récupérez l'extension du fichier
        appreciation_ext = os.path.splitext(appreciation.name)[1]

        # Génération du nom du fichier unique
        appreciation_filename = get_valid_filename(f"{idEtudiant}_appreciation{appreciation_ext}")

        #Enregistrez le fichier avec le nom unique
        appreciation_path = fs.save(appreciation_filename, appreciation)

        for x in etudiants:
            # Associez le rapport à l'étudiant
            x.rapport.appreciation = appreciation_path

            # Mettre le statut en refusé
            x.rapport.statutRapport = "Refusé"

            # Sauvegardez le rapport dans la base de données
            x.rapport.save()

            # Sauvegardez également l'étudiant pour mettre à jour la relation
            x.save()

        # Renvoyez un message de confirmation
        messages.success(request, 'Appréciation envoyée avec succès.')


        is_superuser = check_superuser(request)

        # Stockez l'information dans la session
        request.session['load_rapport'] = True

        # Redirigez vers la vue navbar
        return HttpResponseRedirect(reverse('navbar'))

def rapport_valide(request,idEtudiant):
    typevar = request.GET.get("type")
    
    # Récupérez l'étudiant
    etudiant = Etudiant.objects.get(idEtudiant=idEtudiant)
    
    #Changer le statut du rapport
    etudiant.rapport.statutRapport = "Validé"
    etudiant.rapport.appreciation = None
    etudiant.rapport.save()

    #Changer le statut du stage
    etudiant.stage.statut = "Terminé"
    etudiant.stage.save()

    messages.success(request, 'Rapport validé.')
    return HttpResponseRedirect(reverse('rapport_search') + f'?type={typevar}')

def rapport_refuse(request,idEtudiant):
    typevar = request.GET.get("type")

    # Récupérez l'étudiant
    etudiant = Etudiant.objects.get(idEtudiant=idEtudiant)
    
    #Changer le statut du rapport
    etudiant.rapport.statutRapport = "Refusé"
    etudiant.rapport.save()

    messages.success(request, 'Rapport refusé.')
    return HttpResponseRedirect(reverse('rapport_search') + f'?type={typevar}')

def grilleEval(request,idEtudiant):
    typevar = request.GET.get("type")

    etudiant = Etudiant.objects.get(idEtudiant=idEtudiant)
    etudiants = Etudiant.objects.filter(stage__idStage=etudiant.stage.idStage)
    # Vérifiez si l'utilisateur est connecté et est un superutilisateur
    is_superuser = check_superuser(request)

    context = {
        'is_superuser': is_superuser,
        'etudiants':etudiants,
        'type':typevar
    }
    return render(request,'grilleEval.html',context)

def grilleEval2(request,idEtudiant):
    typevar = request.GET.get("type")

    etudiant = Etudiant.objects.get(idEtudiant=idEtudiant)
    # Vérifiez si l'utilisateur est connecté et est un superutilisateur
    is_superuser = check_superuser(request)

    context = {
        'is_superuser': is_superuser,
        'etudiant':etudiant,
        'type':typevar
    }
    return render(request,'grilleEval2.html',context)

def fichetech(request,idStage):
    typevar = request.GET.get("type")

    etudiants = Etudiant.objects.filter(stage__idStage=idStage)
    e1=etudiants[0]
    e2=""
    if len(etudiants) >= 2:
        e2=etudiants[1]
    else:
        e2=None

    # Vérifiez si l'utilisateur est connecté et est un superutilisateur
    is_superuser = check_superuser(request)

    context = {
        'is_superuser': is_superuser,
        'e1': e1,
        'e2': e2,
        'type': typevar,
    }
    return render(request,'fichetech.html',context)

def attestation(request,idEtudiant):
    typevar = request.GET.get("type")

    etudiant = Etudiant.objects.get(idEtudiant=idEtudiant)
    if etudiant.stage.destinataire == "DSI":
        dest1 = "DIRECTION DES SYSTEMES D'INFORMATION"
        dest2 = "Systèmes d'Information"
    elif etudiant.stage.destinataire == "DRH":
        dest1 = "DIRECTION DES RESSOURCES HUMAINES"
        dest2 = "Ressources Humaines"
    else:
        dest1 = "DIRECION DES AFFAIRES FINANCIERES"
        dest2 = "Affaires Financières"  

    # Obtenir la date actuelle
    date_actuelle = date.today()

    #obtenir la durée du stage
    dateD

    # Vérifiez si l'utilisateur est connecté et est un superutilisateur
    is_superuser = check_superuser(request)

    context = {
        'is_superuser': is_superuser,
        'etudiant': etudiant,
        'dest1' : dest1,
        'dest2' : dest2,
        'date_actuelle' : date_actuelle,
        'type': typevar,
    }
    return render(request,'attestation.html',context)

def user(request):

    # Vérifiez si l'utilisateur est connecté et est un superutilisateur
    is_superuser = check_superuser(request)

    users = CustomUser.objects.all()
    context = {
        'users': users,
        'type': 'Tout',
        'is_superuser': is_superuser
    }
    return render(request, 'user.html', context)

def user_membre(request):
    # Vérifiez si l'utilisateur est connecté et est un superutilisateur
    is_superuser = check_superuser(request)

    users = CustomUser.objects.filter(is_superuser=False)
    context = {
        'users': users,
        'type': 0,
        'is_superuser': is_superuser
    }
    return render(request, 'user.html', context)

def user_admin(request):
    # Vérifiez si l'utilisateur est connecté et est un superutilisateur
    is_superuser = check_superuser(request)

    users = CustomUser.objects.filter(is_superuser=True)
    context = {
        'users': users,
        'type': 1,
        'is_superuser': is_superuser
    }
    return render(request, 'user.html', context)

def user_search(request):
    param = request.GET.get("param")
    typevar = request.GET.get("type")

    # Vérifiez si l'utilisateur est connecté et est un superutilisateur
    is_superuser = check_superuser(request)
    
    if param and typevar:
        # Initialisez le filtre avec une condition vide
        filter_condition = Q()
        # Vérifiez si le paramètre est un nombre (idEtudiant)
        if param.isdigit():
            filter_condition |= Q(id=param)
        else:
            # Le paramètre n'est pas un nombre, donc filtre par nom ou prénom
            filter_condition |= Q(username__icontains=param) 
        
        if typevar != "Tout":
            users = CustomUser.objects.filter(
                filter_condition,
                is_superuser=typevar
            )
        else:
            users = CustomUser.objects.filter(filter_condition)
           
    else:
        if typevar == "Tout":
            users = CustomUser.objects.all()
        else:
            users = CustomUser.objects.filter(is_superuser=typevar)

    context = {
        'users': users,
        'type' : typevar,
        'is_superuser': is_superuser
    }

    return render(request, 'user.html', context)

def delete_user(request,id):
    user = CustomUser.objects.get(id=id)

    if user:
        user.delete()
        messages.success(request, 'La suppression a réussie.')
    return HttpResponseRedirect(reverse('user'))

def personnel(request):
    # Vérifiez si l'utilisateur est connecté et est un superutilisateur
    is_superuser = check_superuser(request)

    personnels = Personnel.objects.all()
    context = {
        'personnels': personnels,
        'is_superuser': is_superuser
    }
    print(is_superuser)
    return render(request, 'personnel.html', context)

def personnel_search(request):
    param = request.GET.get("param")

    # Vérifiez si l'utilisateur est connecté et est un superutilisateur
    is_superuser = check_superuser(request)
    
    if param:
        # Initialisez le filtre avec une condition vide
        filter_condition = Q()
        # Vérifiez si le paramètre est un nombre (idEtudiant)
        if param.isdigit():
            filter_condition |= Q(idPersonnel=param)
        else:
            # Le paramètre n'est pas un nombre, donc filtre par nom ou prénom
            filter_condition |= Q(nomPersonnel__icontains=param) | Q(prenomPersonnel__icontains=param) | Q(im__icontains=param)
        
        personnels = Personnel.objects.filter(
                filter_condition
        )
          
    else:
        personnels = Personnel.objects.all()


    context = {
        'personnels': personnels,
        'is_superuser': is_superuser
    }

    return render(request, 'personnel.html', context)

def formulaire_personnel(request):
    return render(request,'formulaire_personnel.html')

def ajouter_personnel(request):
    if request.method == 'POST':
        im = request.POST.get('im')
        nomPersonnel = request.POST.get('nomPersonnel')
        prenomPersonnel = request.POST.get('prenomPersonnel')
        telephonePersonnel = request.POST.get('telephonePersonnel')
        emailPersonnel = request.POST.get('emailPersonnel')

        # récupérer l'utilisateur
        user = request.user if request.user.is_authenticated else None

        #Créer l'instance du personnel
        personnel = Personnel(im=im,nomPersonnel=nomPersonnel,prenomPersonnel=prenomPersonnel,telephonePersonnel=telephonePersonnel,emailPersonnel=emailPersonnel,user=user)

        # Enregistrer le personnel
        personnel.save()

        # Renvoyez un message de confirmation
        messages.success(request, 'Encadreur ajouté.')

        # Stockez l'information dans la session
        request.session['load_personnel'] = True

        # Redirigez vers la vue navbar
        return redirect('navbar')

def affecter_personnel(request, idPersonnel):
    idEtudiant = request.GET.get('param')

    if idEtudiant:
        try:
            # Récupérer l'étudiant
            etudiant = Etudiant.objects.get(idEtudiant=idEtudiant,stage__statut="Accepté")
            etudiants = Etudiant.objects.filter(stage__idStage=etudiant.stage.idStage)
            

            # Récupérer le personnel
            personnel = Personnel.objects.get(idPersonnel=idPersonnel)
        
            # Affecter un encadreur
            for x in etudiants:
                x.personnel = personnel
                x.save()

            # Renvoyer un message de confirmation
            messages.success(request, 'Affectation réussie.')

            # Stocker l'information dans la session
            request.session['load_personnel'] = True

            # Rediriger vers la vue navbar
            return redirect('personnel')
        except Etudiant.DoesNotExist:
            # Utiliser messages.error pour indiquer une erreur
            messages.error(request, 'Étudiant non trouvé. Veuillez saisir un identifiant valide.')

        # Rediriger vers la vue navbar
        return redirect('personnel')
    else:
        # Utilisation de messages.error pour indiquer une erreur
        messages.error(request, 'Veuillez saisir correctement l\'identifiant de l\'étudiant')

        # Redirigez vers la vue navbar
        return redirect('personnel')
    
def delete_personnel(request,idPersonnel):
    personnel = Personnel.objects.get(idPersonnel=idPersonnel)

    # # Rendre null le personnel lié aux étudiants
    # etudiants = Etudiant.objects.filter(personnel__idPersonnel=idPersonnel)
    # etudiants.personnel=None
    # etudiants.save()

    # Supprimer le personnel
    personnel.delete()

    messages.success(request, 'La suppression a réussie.')
    return HttpResponseRedirect(reverse('personnel'))


def autre(request):
    etudiants = Etudiant.objects.all()
    context = {
        'stagiaires': 'Autre'
    }
    return render(request, 'autre.html', context)


def custom_login(request):
    if request.method == 'POST':
        print(request.POST)
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Connexion réussie, rediriger l'utilisateur où vous le souhaitez
            login(request, form.get_user())
            return redirect('navbar')
            
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('login')


def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            is_superuser = form.cleaned_data.get('is_superuser')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            User = get_user_model()
            user = User.objects.create_user(username=username, email=email, password=password)
            
            if is_superuser:
                user.is_superuser = True
            user.save()  # Enregistrez l'utilisateur avec les attributs appropriés
            
            # Connectez automatiquement l'utilisateur après la création du compte
            login(request, user)
            
            return redirect('navbar')
    else:
        # Vérifiez si l'utilisateur est connecté et est un superutilisateur
        is_superuser = check_superuser(request)
        form = CustomUserCreationForm()
    return render(request, 'create_user.html', {'form': form,'is_superuser': is_superuser})

# ajouter de nouvelles enregistrements
def addrecord(request):
    if request.method == 'POST':
        user = request.user if request.user.is_authenticated else None

        matricule = request.POST.get('matricule')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        adresse = request.POST.get('adresse')
        ecole = request.POST.get('ecole')

        domaine = request.POST.get('domaine')
        theme = request.POST.get('theme')
        niveau = request.POST.get('niveau')
        dateDebut = request.POST.get('dateDebut')
        dateFin = request.POST.get('dateFin')
        destinataire = request.POST.get('destinataire')

        telephone = request.POST.get('tel')
        email = request.POST.get('email')
        
        # Utilisez request.FILES pour les fichiers
        cv = request.FILES.get('cv') 
        lettreMotiv = request.FILES.get('lettreMotiv')  
        autreFichier = request.FILES.get('autreFichier')  

         # Enregistrez les fichiers dans le répertoire "media/documents"
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'documents'))

        # Récupérez les extensions des fichiers
        cv_ext= os.path.splitext(cv.name)[1]
        lettreMotiv_ext= os.path.splitext(lettreMotiv.name)[1]
        autreFichier_ext= os.path.splitext(autreFichier.name)[1]
 

        # Génération des noms de fichiers uniques
        cv_filename = get_valid_filename(f"{matricule}_{nom}_cv{cv_ext}")
        lettreMotiv_filename = get_valid_filename(f"{matricule}_{nom}_lm{lettreMotiv_ext}")
        autreFichier_filename = get_valid_filename(f"{matricule}_{nom}_autre{autreFichier_ext}")

        # Enregistrez les fichiers avec les noms uniques
        cv_path = fs.save(cv_filename, cv)
        lettreMotiv_path = fs.save(lettreMotiv_filename, lettreMotiv)
        autreFichier_path = fs.save(autreFichier_filename, autreFichier)

        # Création d'une instance de Stage
        stage = Stage(domaine=domaine, theme=theme,niveau=niveau, ecole=ecole,dateDebut=dateDebut, dateFin=dateFin,destinataire=destinataire)
        stage.save()

        # Création d'une instance d'Étudiant associée au stage
        etudiant = Etudiant(matricule=matricule, nomEtudiant=nom, prenomEtudiant=prenom, adresseEtudiant=adresse, telephoneEtudiant=telephone, emailEtudiant=email, stage=stage)
        etudiant.save()

        # Création d'une instance de Demande
        demande = Demande(cv=cv_path, lettreMotiv=lettreMotiv_path, autreFichier=autreFichier_path, etudiant=etudiant, user=user)
        demande.save()

        messages.success(request, 'La demande a été envoyée avec succès.')

        # Stockez l'information dans la session
        request.session['load_demande'] = True


        return HttpResponseRedirect(reverse('navbar'))
    
#pour les binomes
def addrecord2(request):
    if request.method == 'POST':
        user = request.user if request.user.is_authenticated else None

        # etudiant 1
        matricule = request.POST.get('matricule')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        adresse = request.POST.get('adresse')
        telephone = request.POST.get('tel')
        email = request.POST.get('email')

        # Utilisez request.FILES pour les fichiers de l'étudiant 1
        cv = request.FILES.get('cv') 
        lettreMotiv = request.FILES.get('lettreMotiv')  
        autreFichier = request.FILES.get('autreFichier') 

        # Enregistrez les fichiers dans le répertoire "media/documents"
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'documents'))

        # Récupérez les extensions des fichiers de l'étudiant 1
        cv_ext= os.path.splitext(cv.name)[1]
        lettreMotiv_ext= os.path.splitext(lettreMotiv.name)[1]
        autreFichier_ext= os.path.splitext(autreFichier.name)[1]
 

        # Génération des noms de fichiers uniques de l'étudiant 1
        cv_filename = get_valid_filename(f"{matricule}_{nom}_cv{cv_ext}")
        lettreMotiv_filename = get_valid_filename(f"{matricule}_{nom}_lm{lettreMotiv_ext}")
        autreFichier_filename = get_valid_filename(f"{matricule}_{nom}_autre{autreFichier_ext}")

        # Enregistrez les fichiers avec les noms uniques de l'étudiant 1
        cv_path = fs.save(cv_filename, cv)
        lettreMotiv_path = fs.save(lettreMotiv_filename, lettreMotiv)
        autreFichier_path = fs.save(autreFichier_filename, autreFichier)


        # etudiant 2

        matricule2 = request.POST.get('matricule2')
        nom2 = request.POST.get('nom2')
        prenom2 = request.POST.get('prenom2')
        adresse2 = request.POST.get('adresse2')
        telephone2 = request.POST.get('tel2')
        email2 = request.POST.get('email2')

        # Utilisez request.FILES pour les fichiers 
        cv2 = request.FILES.get('cv2') 
        lettreMotiv2 = request.FILES.get('lettreMotiv2')  
        autreFichier2 = request.FILES.get('autreFichier2') 

        # Récupérez les extensions des fichiers
        cv2_ext= os.path.splitext(cv2.name)[1]
        lettreMotiv2_ext= os.path.splitext(lettreMotiv2.name)[1]
        autreFichier2_ext= os.path.splitext(autreFichier2.name)[1]
 

        # Génération des noms de fichiers uniques
        cv2_filename = get_valid_filename(f"{matricule2}_{nom2}_cv{cv2_ext}")
        lettreMotiv2_filename = get_valid_filename(f"{matricule2}_{nom2}_lm{lettreMotiv2_ext}")
        autreFichier2_filename = get_valid_filename(f"{matricule2}_{nom2}_autre{autreFichier2_ext}")

        # Enregistrez les fichiers avec les noms uniques
        cv2_path = fs.save(cv2_filename, cv)
        lettreMotiv2_path = fs.save(lettreMotiv2_filename, lettreMotiv)
        autreFichier2_path = fs.save(autreFichier2_filename, autreFichier)

        ecole = request.POST.get('ecole')
        domaine = request.POST.get('domaine')
        theme = request.POST.get('theme')
        niveau = request.POST.get('niveau')
        dateDebut = request.POST.get('dateDebut')
        dateFin = request.POST.get('dateFin')
        destinataire = request.POST.get('destinataire')


        # Création d'une instance de Stage
        stage = Stage(domaine=domaine, theme=theme,niveau=niveau , dateDebut=dateDebut, ecole=ecole, dateFin=dateFin,destinataire=destinataire)
        stage.save()

        # Création d'une instance d'Étudiant 1 associée au stage
        etudiant = Etudiant(matricule=matricule, nomEtudiant=nom, prenomEtudiant=prenom, adresseEtudiant=adresse, telephoneEtudiant=telephone,emailEtudiant=email, stage=stage)
        etudiant.save()

        # Création d'une instance d'Étudiant 2 associée au stage
        etudiant2 = Etudiant(matricule=matricule2, nomEtudiant=nom2, prenomEtudiant=prenom2, adresseEtudiant=adresse2, telephoneEtudiant=telephone2,emailEtudiant=email2, stage=stage)
        etudiant2.save()

        # Création d'une instance de Demande de l'étudiant 1
        demande = Demande(cv=cv_path, lettreMotiv=lettreMotiv_path, autreFichier=autreFichier_path, etudiant=etudiant, user=user)
        demande.save()

         # Création d'une instance de Demande de l'étudiant 1
        demande2 = Demande(cv=cv2_path, lettreMotiv=lettreMotiv2_path, autreFichier=autreFichier2_path, etudiant=etudiant2, user=user)
        demande2.save()

        messages.success(request, 'La demande a été envoyée avec succès.')

        # Stockez l'information dans la session
        request.session['load_demande'] = True

        return HttpResponseRedirect(reverse('navbar'))


def index1(request):
    template= loader.get_template("myfirst.html")
    return HttpResponse(template.render())

def add(request):
    template=loader.get_template(("add.html"))
    return HttpResponse(template.render({},request))

# def addrecord(request):
#     matricule = request.POST['matricule']
#     idstage = request.POST['idstage']
#     nom = request.POST['nom']
#     prenom = request.POST['prenom']
#     adresse = request.POST['adresse']
#     ecole = request.POST['ecole']
#     filiere = request.POST['filiere']
#     email = request.POST['email']
    
#     etudiant=Etudiant(matricule=matricule,idStage=idstage,nomEtudiant=nom,prenomEtudiant=prenom,adresseEtudiant=adresse,ecole=ecole,filiere=filiere,emailEtudiant=email)
#     etudiant.save()
#     return HttpResponseRedirect(reverse('index'))

#supprimer un enregistrement
def delete(request,numeroDemande):
    typevar = request.GET.get("type")
    demande = Demande.objects.get(numeroDemande=numeroDemande)
    
    # Supprimer l'objet Stage lié
    if demande.etudiant.stage:
        demande.etudiant.stage.delete()

    if demande.etudiant.rapport:    
        demande.etudiant.rapport.delete()

    # Supprimer l'objet Etudiant lié
    if demande.etudiant:
        demande.etudiant.delete()

    # Enfin, supprimer l'objet Demande
    demande.delete()
    messages.success(request, 'La suppression a réussie.')
    return HttpResponseRedirect(reverse('demande_search') + f'?type={typevar}')

#supprimer un rapport
def delete_rapport(request,idEtudiant):
    typevar = request.GET.get("type")
    demande = Demande.objects.get(etudiant__idEtudiant=idEtudiant)
    demandes = Demande.objects.filter(etudiant__stage__idStage=demande.etudiant.stage.idStage)

    for x in demandes:
        if x.etudiant:
            # Supprimer l'objet Stage lié
            if x.etudiant.rapport:
                x.etudiant.rapport.delete() 

            if x.etudiant.stage:
                x.etudiant.stage.delete()


            # Supprimer l'objet Etudiant lié
            x.etudiant.delete()

        # Enfin, supprimer l'objet Demande
        x.delete()
    messages.success(request, 'La suppression a réussie.')
    return HttpResponseRedirect(reverse('rapport_search') + f'?type={typevar}')


#en charge de l'acceptation
def accept(request,numeroDemande):
    typevar = request.GET.get("type")
    demande = Demande.objects.get(numeroDemande=numeroDemande)
    demande.etudiant.stage.statut = "Accepté"
    demande.etudiant.stage.save()
    messages.success(request, 'Stage acceptée.')
    return HttpResponseRedirect(reverse('demande_search') + f'?type={typevar}')

#en cas de refus
def refuse(request,numeroDemande):
    typevar = request.GET.get("type")
    demande = Demande.objects.get(numeroDemande=numeroDemande)
    demande.etudiant.stage.statut = "Refusé"
    demande.etudiant.stage.save()
    messages.success(request, 'Stage refusée.')
    return HttpResponseRedirect(reverse('demande_search') + f'?type={typevar}')

#pour terminer le stage
def termine(request,numeroDemande):
    typevar = request.GET.get("type")
    demande = Demande.objects.get(numeroDemande=numeroDemande)
    demande.etudiant.stage.statut = "Terminé"
    demande.etudiant.stage.save()
    messages.success(request, 'Stage terminée.')
    return HttpResponseRedirect(reverse('demande') + f'?type={typevar}')


#téléchargement des fichiers
def download_file(request, numeroDemande, field_name):
    demande = Demande.objects.get(numeroDemande=numeroDemande)
      # Créez le chemin complet vers le fichier en prenant en compte le sous-dossier "documents"
    if field_name == 'cv':
        print(demande.cv.name)
        file = os.path.join(settings.MEDIA_ROOT, 'documents', demande.cv.name)
    elif field_name == 'lettreMotiv':
        file = os.path.join(settings.MEDIA_ROOT, 'documents', demande.lettreMotiv.name)
    elif field_name == 'autreFichier':
        file = os.path.join(settings.MEDIA_ROOT, 'documents', demande.autreFichier.name)
    else:
        raise Http404("File not found")

    # Ouvrez le fichier en mode binaire
    with open(file, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')

        # Définissez l'en-tête pour forcer le téléchargement
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file)}"'

    return response

#téléchargement du rapport
def download_rapport(request, idEtudiant , field_name):
    # demande = Demande.objects.get(numeroDemande=numeroDemande)
    etudiant = Etudiant.objects.get(idEtudiant=idEtudiant)
      
    # # Créez le chemin complet vers le fichier en prenant en compte le sous-dossier "documents"
    # if field_name == 'cv':
    #     print(demande.cv.name)
    #     file = os.path.join(settings.MEDIA_ROOT, 'documents', demande.cv.name)
    # elif field_name == 'lettreMotiv':
    #     file = os.path.join(settings.MEDIA_ROOT, 'documents', demande.lettreMotiv.name)
    # elif field_name == 'autreFichier':
    #     file = os.path.join(settings.MEDIA_ROOT, 'documents', demande.autreFichier.name)
    # else:
    #     raise Http404("File not found")
    
    if field_name == 'rapportStage':
        file = os.path.join(settings.MEDIA_ROOT, 'documents', etudiant.rapport.rapportStage.name)
    elif field_name == 'appreciation':
        file = os.path.join(settings.MEDIA_ROOT, 'documents', etudiant.rapport.appreciation.name)
    else:
        raise Http404("File not found")

    # Ouvrez le fichier en mode binaire
    with open(file, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')

        # Définissez l'en-tête pour forcer le téléchargement
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file)}"'

    return response
























def update(request,matricule):
    etudiant = Etudiant.objects.get(matricule=matricule)
    template = loader.get_template('update.html')
    context = {
        'etudiant':etudiant
    }
    return HttpResponse(template.render(context,request))

















def updaterecord(request,matricule):
    matriculeE = request.POST['matricule']
    idstage = request.POST['idstage']
    nom = request.POST['nom']
    prenom = request.POST['prenom']
    adresse = request.POST['adresse']
    ecole = request.POST['ecole']
    filiere = request.POST['filiere']
    email = request.POST['email']
    telephone = request.POST['tel']
    etudiant = Etudiant.objects.get(matricule=matricule)

    
    etudiant.matricule = matriculeE
    etudiant.idStage = idstage
    etudiant.nomEtudiant = nom
    etudiant.prenomEtudiant = prenom
    etudiant.adresseEtudiant = adresse
    etudiant.ecole = ecole
    etudiant.filiere = filiere
    etudiant.emailEtudiant = email

    Etudiant.save()

    return HttpResponseRedirect(reverse('index'))
