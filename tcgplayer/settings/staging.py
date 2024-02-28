import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = True

ALLOWED_HOSTS = ['*']

MAILGUN_SENDER_DOMAIN = "yoor-staging-support@app.cryptto.trade"

sentry_sdk.init(
    dsn="https://e23be818b7c04ef885cbeef8072c6fbe@o983626.ingest.sentry.io/6129512",
    integrations=[DjangoIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)
