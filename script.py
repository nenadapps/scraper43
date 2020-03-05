from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import requests
from time import sleep
import re

base_url = 'https://www.delcampe.net'

def get_html(url):
    
    html_content = ''
    try:
        page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        html_content = BeautifulSoup(page.content, "html.parser")
    except: 
        pass
    
    return html_content

def get_details(url):
    
    stamp = {}
    
    try:
        html = get_html(url)
    except:
        return stamp
    
    try:
        title = html.select('#item h1')[0].get_text().strip()
        title = title.replace('\n', ' ').strip()
        stamp['title'] = title
    except:
        stamp['title'] = None      
    
    try:
        raw_text = html.select('.description')[0].get_text().strip()
        raw_text = re.sub(' +', ' ', raw_text)
        raw_text = raw_text.replace('\n', ' ').strip()
        raw_text = raw_text.replace(u'\xa0', u' ').strip()
        stamp['raw_text'] = raw_text
    except:
        stamp['raw_text'] = None
    
    try:
        price = html.select('#buy-box .price')[0].get_text().strip()
        price = price.replace('€', '').strip()
        stamp['price'] = price
    except:
        stamp['price'] = None  
    
    stamp['currency'] = 'EUR'
    
    # image_urls should be a list
    images = []                    
    try:
        if len(html.select('.img-container img')):
            image_items = html.select('.img-container img')
        else:
            image_items = html.select('img.img-lense')

        for image_item in image_items:
            img = image_item.get('src').replace('/img_small/', '/img_large/').replace('/micro/', '/large/')
            if img not in images:
                images.append(img)
    except:
        pass
    
    stamp['image_urls'] = images 
        
    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date
    
    stamp['url'] = url
    
    print(stamp)
    print('+++++++++++++')
    sleep(randint(25, 65))
           
    return stamp

def get_page_items(url):

    items = []
    next_url = ''

    try:
        html = get_html(url)
    except:
        return items, next_url

    try:
        for item in html.select('.item-link'):
            item_link = base_url + item.get('href')
            if item_link not in items:
                items.append(item_link)
    except:
        pass
    
    try:
        next_url_cont = html.select('a.next')[0]
        next_url_href = next_url_cont.get('href')
        if next_url_href:
            next_url = base_url + next_url_href
    except:
        pass
   
    shuffle(list(set(items)))
    
    return items, next_url

def get_main_categories():
    
    url = 'https://www.delcampe.net/en_GB/collectables/category'
   
    items = {}

    try:
        html = get_html(url)
    except:
        return items

    try:
        for item in html.select('#categories-list section.category-bloc .category-bloc-list .col-md-6 > ul > li > a'):
            item_link = base_url + item.get('href')
            item_text = item.get_text().replace('...', '').strip()
            if (item_link not in items) and ('/search' not in item_link): 
                items[item_text] = item_link
    except: 
        pass
    
    shuffle(list(set(items)))
    
    return items

def get_categories(url):
   
    items = []

    try:
        html = get_html(url)
    except:
        return items

    try:
        for item in html.select('#categories-list section.category-bloc .category-bloc-list .col-md-6 > ul > li > a'):
            item_link = base_url + item.get('href')
            if (item_link not in items) and ('/search' not in item_link): 
                items.append(item_link)
    except: 
        pass
    
    shuffle(list(set(items)))
    
    return items


item_dict = get_main_categories()

for key in item_dict:
    print(key + ': ' + item_dict[key])   

selection = input('Choose category: ')

selected_main_category = item_dict[selection]

categories = get_categories(selected_main_category)   
for category in categories:
    print(category)
    choice = input("Do you want to scrape this?")
    if choice == 'Y':
        pass
    else:
        continue
    subcategories = get_categories(category) 
    for subcategory in subcategories:
        page_url = subcategory
        while(page_url):
            page_items, page_url = get_page_items(page_url)
            for page_item in page_items:
                stamp = get_details(page_item) 
