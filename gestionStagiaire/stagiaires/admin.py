from django.contrib import admin
from .models import Stage,Etudiant

class EtudiantAdmin(admin.ModelAdmin):
    list_display = ("matricule", "get_stage_id", "nomEtudiant", "prenomEtudiant", "adresseEtudiant", "emailEtudiant")

    def get_stage_id(self, obj):
        if obj.stage:
            return obj.stage.idStage
        else:
            return "null"

    get_stage_id.short_description = "id du stage"  # Renommez la colonne dans l'interface admin

class StageAdmin(admin.ModelAdmin):
    list_display = ("idStage","domaine","theme","dateDebut","dateFin","statut")

admin.site.register(Stage,StageAdmin)
admin.site.register(Etudiant, EtudiantAdmin)

