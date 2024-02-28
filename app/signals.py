
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from app.models import Card
from app.tasks import fetch_link_from_list, scrape_data_from_tcgplayer

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Card)
def handle_post_save_card(sender, instance, created, **kwargs):
    """
    Start fetching data for the input link
    """

    if created:
        if '/search/' in instance.card_link:
            # this is a list
            instance.category = 'list'
            instance.save()
            fetch_link_from_list.delay(instance.id)
        else:
            if instance.run_immediately is True:
                scrape_data_from_tcgplayer.delay(instance.id)
