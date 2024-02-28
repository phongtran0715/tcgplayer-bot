# Pokémon Card Monitor and Sync Bot

## Description

This project is a Python Django application designed to monitor Pokémon card statuses, including stock availability on the TCGPlayer website, and clone that card data. Additionally, the bot supports pushing Pokémon card data from TCGPlayer to a Shopify store, facilitating seamless product management and synchronization between platforms.

## Features

- **Card Monitoring**: Tracks Pokémon card availability and other status changes on TCGPlayer in real-time.
- **Data Cloning**: Clones card data from TCGPlayer for local storage or processing.
- **Shopify Integration**: Automatically pushes updated Pokémon card data from TCGPlayer to your Shopify store.
- **Django Admin Interface**: Manage and monitor the bot's operations through a user-friendly Django admin interface.
- **Automated Synchronization**: Ensures your Shopify store remains up-to-date with the latest Pokémon card releases and restocks.

## Getting Started

### Prerequisites

- Python 3.x
- Django
- Requests (for API calls)
- A Shopify store with API access enabled

### Installation

1. Clone the repository to your local machine:
`git clone https://github.com/phongtran0715/tcgplayer-bot`

2. Navigate to the cloned directory:
`cd tcgplayer-bot`

3. Install the required Python dependencies:
`pip install -r requirements.txt`


### Configuration

1. Set up your `settings.py` in the Django project to include your TCGPlayer and Shopify API credentials.
2. Configure the card monitoring criteria (e.g., specific Pokémon cards, categories) in the Django admin panel.

### Running the Application

To start the Django application, run:

`python manage.py runserver`


Navigate to the Django admin panel to start monitoring and manage your settings.


## Contact

Phong Tran - Telegram: @phongtran0715 - Skype: @phongtran0715

Project Link: [https://github.com/phongtran0715/tcgplayer-bot](https://github.com/phongtran0715/tcgplayer-bot)
