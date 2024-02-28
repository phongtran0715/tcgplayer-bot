from tcgplayer.celery_app import app

app.conf.beat_schedule = {
    'scrape_card_info': {
        'task': 'app.tasks.scrape_card_info',
        'schedule': 40,  # Run every 40 seconds
    },
}

app.conf.timezone = 'UTC'
