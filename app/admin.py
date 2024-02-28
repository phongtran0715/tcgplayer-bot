from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from preferences.admin import PreferencesAdmin

from .models import Card, MyPreferences


class CardResource(resources.ModelResource):
    class Meta:
        model = Card
        import_id_fields = ('tcgplayer_id',)
        export_order = ('id', 'title', 'card_link', 'quantity', 'tcgplayer_id', 'shopify_id', 'description', 'picture',
                        'category', 'price', 'shipping_price', 'presale_item', 'presale_note_text', 'seller', 'condition', 'is_scrape', 'run_immediately', 'is_upload', 'scrape_time'
                        )

    def before_import_row(self, row, **kwargs):
        row['run_immediately'] = False
        return row


class CardAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = CardResource

    list_display = ['id', 'tcgplayer_id', 'shopify_id', 'title', 'card_link', 'quantity', 'category',
                    'price', 'is_scrape', 'is_upload', 'created', 'modified']
    search_fields = ('title',)
    list_filter = ('is_scrape', 'is_upload', 'category', 'created',)
    search_fields = ('title', 'tcgplayer_id')

    fieldsets = (
        ('Inputs', {
            'fields': ('card_link', 'quantity', 'discount_percentage')
        }),
        ('Readonly fields', {
            'fields': [field.name for field in Card._meta.get_fields() if field.name not in ('id', 'card_link', 'quantity', 'created', 'modified', 'discount_percentage')]
        }))


class MyPreferenceAdmin(PreferencesAdmin):
    readonly_fields = ["import_example_file", ]


admin.site.register(Card, CardAdmin)
admin.site.register(MyPreferences, MyPreferenceAdmin)
