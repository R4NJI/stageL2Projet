from django.db.models.signals import Signal
from django.dispatch import receiver
from datetime import date
from .models import Stage

stage_date_expired = Signal()

@receiver(stage_date_expired)
def handle_stage_date_expired(sender, **kwargs):
    today = date.today()
    expired_stages = Stage.objects.filter(dateFin__lt=today,statut="Accepté")
    print(today)
    print("signal déclenché:",expired_stages)
    
    for stage in expired_stages:
        # Faites ce que vous voulez pour chaque stage expiré, par exemple :
        stage.statut = 'Expiré'
        stage.save()
