from django.db import models
from django_extensions.db.models import TimeStampedModel

from preferences.models import Preferences

CATEGORY_LIST = [
    ('list', 'List'),
    ('sealed', 'Sealed'),
    ('single_card', 'Single Card')
]


class Card(TimeStampedModel, models.Model):
    card_link = models.URLField(max_length=512, blank=True, null=True)
    title = models.CharField(
        max_length=512, blank=True, null=False, default="")
    picture = models.CharField(
        max_length=512, blank=True, null=False, default="")
    description = models.TextField(blank=True, null=True)
    category = models.CharField(
        max_length=64, choices=CATEGORY_LIST, blank=True, null=False, default="")
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    shipping_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    release_date = models.DateTimeField(blank=True, null=True)
    quantity = models.IntegerField(default=1, null=True, blank=True)
    presale_item = models.BooleanField(default=False)
    presale_note_text = models.TextField(blank=True, null=True)
    seller = models.CharField(max_length=64, blank=True, null=True, default="")
    condition = models.CharField(
        max_length=64, blank=True, null=False, default="")
    is_scrape = models.BooleanField(default=False)
    run_immediately = models.BooleanField(default=True)
    is_upload = models.BooleanField(default=False)
    scrape_time = models.IntegerField(default=0)
    tcgplayer_id = models.CharField(
        max_length=64, blank=True, null=True, default="")
    shopify_id = models.CharField(
        max_length=64, blank=True, null=True, default="")
    discount_percentage = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Card Links'
        db_table = 'card_links'
        ordering = ['-modified']
        indexes = [
            models.Index(fields=['title', 'category'])
        ]


class MyPreferences(Preferences):
    shopify_api_key = models.CharField(
        max_length=128, blank=False, null=False, default="")
    shopify_secret_key = models.CharField(
        max_length=128, blank=False, null=False, default="")
    shopify_url = models.URLField(
        max_length=512, blank=False, null=False)
    shopify_access_token = models.CharField(
        max_length=128, blank=False, null=False, default="")
    location_id = models.CharField(
        max_length=128, blank=False, null=False, default="", help_text=("Shopify inventory location id"))
    import_example_file = models.URLField(
        default="https://drive.google.com/file/d/1XiWO6nLRIGyxE5266jbn2iY40ieYvbnN/view?usp=sharing", help_text="Download importing template file"
    )

    class Meta:
        verbose_name_plural = 'Preferences'
