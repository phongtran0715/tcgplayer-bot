import logging
import re
import ssl
import time

import shopify
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from preferences import preferences
from tcgplayer.celery_app import app

from .models import Card
from .serializers import CardSerializers

from.tag_generator.tagger import get_tag_from_text
logger = logging.getLogger(__name__)


def extract_text(soup_obj, tag, attribute_name, attribute_value):
    txt = soup_obj.find(tag, {attribute_name: attribute_value}).text.strip() if soup_obj.find(tag, {attribute_name: attribute_value}) else ''
    return txt


@app.task
def scrape_data_from_tcgplayer(card_id):
    """
    Fetch card data from tcgplayer
    """
    card = Card.objects.get(id=card_id)
    delay = 30
    quantity = card.quantity
    seller = None
    shipping_price = 0.0
    title = None
    condition = ''
    description = None
    price = 0.0
    img_src = ''
    presale_item = False
    presale_note_text = None
    category = ''

    tcgplayer_id = card.card_link.split('product/')[1].split('/')[0]

    logging.info("Start fetching url: {}".format(card.card_link))

    driver = webdriver.Remote(command_executor="http://firefox:4444/wd/hub", desired_capabilities=DesiredCapabilities.FIREFOX)
    driver.get(card.card_link)
    time.sleep(10)
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'spotlight')))
    except TimeoutException:
        logger.info("=====> Could not init driver")
        raise Exception("Loading exceeds delay time")
    else:
        dropdown = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/section[2]/section/section[2]/section/div/span/span[2]/div/select')
        dropdown.click()
        select = Select(driver.find_element(By.XPATH, '//*[@id="app"]/div/div/section[2]/section/section[2]/section/div/span/span[2]/div/select'))
        select.select_by_value("50")
        dropdown1 = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/section[2]/section/section[2]/section/div/span/span[1]/div/select')
        dropdown1.click()
        select2 = Select(driver.find_element(By.XPATH, '//*[@id="app"]/div/div/section[2]/section/section[2]/section/div/span/span[1]/div/select'))
        select2.select_by_value("price")
        time.sleep(10)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        driver.quit()
        #get title of card
        title = soup.title.string
        #generate tags from title
        tags = get_tag_from_text(title)
        # get card detail
        div_detail = soup.find('div', {'class': 'product__item-details__container'})
        if div_detail is not None:
            # description = extract_text(div_detail, 'ul', 'class', 'product__item-details__attributes')
            # description = description + extract_text(div_detail, 'div', 'class', 'product__item-details__description')
            description = div_detail.find('div', {'class': 'product__item-details__content'})

        #get card image
        img_section = soup.find('section', {'class': {'image-set__grid fit-contain'}})
        img_src = img_section.find('img')['src']
        #get category
        latest_sale = soup.find('section', {'class': 'latest-sales price-guide__latest-sales'})
        ul_latest_sale = latest_sale.find('ul')
        condition_in_latest_sale = extract_text(ul_latest_sale, 'span', 'class', 'condition')
        category_single_card = ('nm', 'lp', 'near mint', 'lightly played', 'mp')
        if any(x in condition_in_latest_sale.lower() for x in category_single_card):
            category = 'single_card'
            tags += "single_card, "
        if 'unopened' in condition_in_latest_sale.lower():
            category = 'sealed'
            tags += 'sealed, '
        #get card type:
        breadcrumbs = soup.find('div', {'class': 'breadcrumbs'})
        card_type = breadcrumbs.find_all('a')[1].text.strip()
        tags += card_type.lower() + ', '
        #get collection:
        div_collection = soup.find('div', {'class': 'product-details__name__sub-header__links'})
        collection = div_collection.find('span').text.strip() if div_collection.find('span') else "Unknown"
        tags += collection + ', '
        collection = card_type + ' - ' + collection
        tags += collection + ', '

        #check if any one selling this card
        no_listing = soup.find('section', {'class': 'no-result spotlight__no-listings'})
        if no_listing is None:
            #find the best condition for card
            near_min_product = find_near_mint_price(soup)
            condition = near_min_product['condition']
            seller = near_min_product['seller']
            price = near_min_product['price']
            shipping_price = near_min_product['shipping_price']
            description = f'<h3><strong><span style="color: #ff2a00;">Condition: {condition}</span></strong></h3>' + str(description)
        else:
            #get market price and set quantity to 0 when there is no listing
            div_market_price = soup.find('ul', {'class': 'price-points__rows'})
            market_price_row = div_market_price.find('li')
            price = market_price_row.find('span', {'class': 'price'}).text.strip().replace('$', '')
            if price == '-':
                price = 0.0
            description = f'<h3><strong><span style="color: #ff2a00;">Condition: {condition_in_latest_sale}</span></strong></h3>' + str(description)
            quantity = 0
        #check presale item
        if soup.find('section', {'class': 'presale-note-header'}) is not None:
            presale_item = True
            presale_note_text = extract_text(soup, 'span', 'class', 'presale-note__text')
            presale_note_html = str(soup.find('span', {'class': 'presale-note__text'})).replace('<span class="presale-note__text"', '<span class="presale-note__text" style="color: #ff2a00;"')
            description = presale_note_html + '<p style="color: #ff2a00;">And delivery time is not always be the same, it depends on your locations</p>' + str(description)

    price = float(price) * ((100 - float(card.discount_percentage)) / 100) if card.discount_percentage != 0.0 else float(price)
    data = {
        'seller': seller,
        'shipping_price': shipping_price,
        'price': str(round(price, 2)),
        'title': title,
        'condition': condition,
        'description': str(description),
        'quantity': quantity,
        'is_scrape': True,
        'picture': img_src,
        'presale_item': presale_item,
        'presale_note_text': presale_note_text,
        'category': category,
        'tcgplayer_id': tcgplayer_id,
        'scrape_time': card.scrape_time + 1,
        'collection': collection,
        'tags': tags,
        'discount_percentage': card.discount_percentage,
        'card_type': card_type,
    }

    #check exists card with tcgplayer_id
    old_card = Card.objects.filter(tcgplayer_id=tcgplayer_id).first()
    if old_card and old_card.is_upload is True:
        #update the old card instance
        data['is_upload'] = True
        data['shopify_id'] = old_card.shopify_id
        serializer = CardSerializers(data=data, instance=card, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        update_listing_shopify(data)
    else:
        shopify_product = add_product_to_shopify(data)
        if shopify_product:
            data['is_upload'] = True
            data['shopify_id'] = shopify_product.id
        #update the new card instance
        serializer = CardSerializers(data=data, instance=card, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

    logging.info("Finish fetching.")


@app.task
def fetch_link_from_list(card_id):
    """
    Fetch card links from card products list
    """
    delay = 30
    tcgplayer_base_url = 'https://www.tcgplayer.com'
    title = ''

    card = Card.objects.get(id=card_id)
    list_url = re.sub(r"\b&page=\b\d{1,2}", "", card.card_link)
    logger.info("Start fetching url: {}".format(card.card_link))
    options = Options()
    options.headless = True
    options.add_argument("--start-maximized")
    driver = webdriver.Remote(command_executor="http://firefox:4444/wd/hub", desired_capabilities=DesiredCapabilities.FIREFOX, options=options)
    driver.get(card.card_link.split('&Condition=')[0])

    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'search-results')))
        time.sleep(5)
    except TimeoutException:
        logger.info("Loading exceeds delay time")
    else:
        soup = BeautifulSoup(driver.page_source, 'lxml')
        pagination_buttons = soup.find_all('button', {'class': 'pagination-button'})
        last_pagination = pagination_buttons[-1]['data-testid'].split('__')[1]
        applied_filters = soup.find_all('span', {'class': 'dismiss-bubble filter-bubbles__bubble'})
        for filter in applied_filters:
            title = title + filter.text.strip() + ', '
        data = {
            'title': title,
            'card_link': list_url,
            'is_scrape': True
        }
        serializer = CardSerializers(data=data, instance=card, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        for page in range(1, int(last_pagination) + 1):
            page_url = list_url + "&page" + str(page)
            driver.implicitly_wait(10)
            driver.get(page_url)

            try:
                WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'search-results')))
            except TimeoutException:
                logger.info('Loading exceeds delay time')
                break
            else:
                soup = BeautifulSoup(driver.page_source, 'lxml')
                div_search_res = soup.find_all('div', {'class': 'search-result'})
                for search_res in div_search_res:
                    a_tag = search_res.find('a')
                    card_link = tcgplayer_base_url + a_tag['href']
                    tcgplayer_id = card_link.split('product/')[1].split('/')[0]
                    new_data = {
                        'card_link': card_link,
                        'run_immediately': False,
                        'is_scrape': False,
                        'tcgplayer_id': tcgplayer_id
                    }
                    serializers = CardSerializers(data=new_data)
                    if serializers.is_valid(raise_exception=True):
                        serializers.save()
                driver.implicitly_wait(10)

    driver.quit()


@app.task
def scrape_card_info():
    """
    Get card which was not scraped from database
    Scrape card info
    """

    # get all un-scraped link
    card = Card.objects.filter(run_immediately=False, is_scrape=False).first()
    if card:
        scrape_data_from_tcgplayer.delay(card.id)
    else:
        pass


def add_product_to_shopify(data):
    """
    Upload card to shopify through ShopifyAPI
    """

    shopify_api_key = preferences.MyPreferences.shopify_api_key
    shopify_secret_key = preferences.MyPreferences.shopify_secret_key
    shopify_url = preferences.MyPreferences.shopify_url
    shopify_access_token = preferences.MyPreferences.shopify_access_token
    location_id = preferences.MyPreferences.location_id
    api_version = '2022-07'
    if shopify_api_key and shopify_secret_key and shopify_url and shopify_access_token and location_id:
        shopify.Session.setup(api_key=shopify_api_key, secret=shopify_secret_key)
        session = shopify.Session(shopify_url, api_version, shopify_access_token)
        shopify.ShopifyResource.activate_session(session)
        logging.info("Start session uploading product to shopify")
        # init new product
        new_product = shopify.Product()
        new_product.title = data['title']
        new_product.body_html = data['description']
        new_product.vendor = data['card_type']
        new_product.product_type = 'Collectible Trading Cards'
        new_product.tags = data['tags']
        #find exists collection or create new
        collections = shopify.CustomCollection.find(title=data['collection'])
        if collections:
            collection_id = collections[0].id
        else:
            collection = shopify.CustomCollection()
            collection.title = data['collection']
            collection.body_html = f"<p>This is {data['collection']}collections</p>"
            collection.published = True
            collection.save()
            collection_id = collection.id

        #add image to product
        image = shopify.Image()
        image.src = data['picture']
        new_product.images = [image]
        #get price after discount

        #add variants to product
        variant = shopify.Variant()
        variant.price = data['price']
        variant.requires_shipping = True
        variant.inventory_management = "shopify"
        variant.taxable = False
        if data['category'] == 'single_card':
            variant.weight = 4
            variant.weight_unit = 'oz'
        elif data['category'] == 'sealed':
            variant.weight = 4
            variant.weight_unit = 'lb'

        new_product.variants = [variant]
        #save product
        res = new_product.save()
        #save Inventory quantity for product
        shopify.InventoryLevel.set(
            inventory_item_id=new_product.variants[0].inventory_item_id,
            location_id=location_id,
            available=data['quantity']
        )
        #add product to collection
        add_collection = shopify.Collect({
            'product_id': new_product.id,
            'collection_id': collection_id
        })
        res1 = add_collection.save()

        shopify.ShopifyResource.clear_session()
        logging.info("Upload complete")
        if res is True and res1 is True:
            return new_product
        else:
            logger.info(res.errors.full_messages())
            return None
    else:
        return None


def update_listing_shopify(data):
    """
    Update info of product on shopify
    """

    shopify_api_key = preferences.MyPreferences.shopify_api_key
    shopify_secret_key = preferences.MyPreferences.shopify_secret_key
    shopify_url = preferences.MyPreferences.shopify_url
    shopify_access_token = preferences.MyPreferences.shopify_access_token
    location_id = preferences.MyPreferences.location_id
    api_version = '2022-07'
    ssl._create_default_https_context = ssl._create_unverified_context
    if shopify_api_key and shopify_secret_key and shopify_url and shopify_access_token and location_id:
        shopify.Session.setup(api_key=shopify_api_key, secret=shopify_secret_key)
        session = shopify.Session(shopify_url, api_version, shopify_access_token)
        shopify.ShopifyResource.activate_session(session)

        product_shopify_id = data['shopify_id']
        product_shopify = shopify.Product.find(str(product_shopify_id))
        #update info
        product_shopify.title = data['title']
        product_shopify.body_html = data['description']
        product_shopify.tags = data['tags']

        product_shopify.variants[0].price = data['price']
        if product_shopify.status.lower() == 'draft':
            product_shopify.status = 'active'

        if product_shopify.variants[0].weight == float(0):
            if data['category'] == 'single_card':
                product_shopify.variants[0].weight = 4
                product_shopify.variants[0].weight_unit = 'oz'
            elif data['category'] == 'sealed':
                product_shopify.variants[0].weight = 4
                product_shopify.variants[0].weight_unit = 'lb'

        product_shopify.save()
        inventory_item_id = product_shopify.variants[0].inventory_item_id

        res = shopify.InventoryLevel.adjust(location_id=location_id, inventory_item_id=inventory_item_id, available_adjustment=data['quantity'])

        shopify.ShopifyResource.clear_session()
        return res
    else:
        pass


def find_near_mint_price(soup_obj):

    condition = ''
    price = 0.0
    seller = ''
    shipping_price = 0.0
    near_mint_list = []
    lightly_played_list = []
    moderately_played_list = []
    heavily_played_list = []
    other_list = []

    listing = soup_obj.find_all('section', {'class': 'listing-item product-details__listings-results'})
    for card in listing:
        if 'near mint' in card.find('h3', {'class': 'listing-item__condition'}).text.strip().lower():
            near_mint_list.append(card)
        elif 'lightly played' in card.find('h3', {'class': 'listing-item__condition'}).text.strip().lower():
            lightly_played_list.append(card)
        elif 'moderately played' in card.find('h3', {'class': 'listing-item__condition'}).text.strip().lower():
            moderately_played_list.append(card)
        elif 'heavily played' in card.find('h3', {'class': 'listing-item__condition'}).text.strip().lower():
            heavily_played_list.append(card)
        else:
            other_list.append(card)

    my_list = []
    if len(near_mint_list) > 0:
        my_list = near_mint_list
    elif len(lightly_played_list) > 0:
        my_list = lightly_played_list
    elif len(moderately_played_list) > 0:
        my_list = moderately_played_list
    elif len(heavily_played_list) > 0:
        my_list = heavily_played_list
    elif len(other_list) > 0:
        my_list = other_list

    if len(my_list) > 0:
        condition = extract_text(my_list[0], 'h3', 'class', 'listing-item__condition')
        seller = extract_text(my_list[0], 'a', 'class', 'seller-info__name')
        obj = my_list[0].find('div', {'class': 'listing-item__price'})
        price = obj.text.strip().replace('$', '') if obj else 0.0
        tmp = my_list[0].find('span', {'class': 'shipping-messages__price'})
        shipping_price = tmp.text.strip().split(' ')[1].replace('$', '') if tmp else 0.0

    return {
        'condition': condition,
        'seller': seller,
        'price': price,
        'shipping_price': shipping_price,
    }
