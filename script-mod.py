from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import requests
from time import sleep
import re
'''
from fake_useragent import UserAgent
import os
import sqlite3
import shutil
from stem import Signal
from stem.control import Controller
import socket
import socks

controller = Controller.from_port(port=9051)
controller.authenticate()'''
req = requests.Session()
'''
def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5 , "127.0.0.1", 9050)
    socket.socket = socks.socksocket

def renew_tor():
    controller.signal(Signal.NEWNYM)
    
UA = UserAgent(fallback='Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2')
hdr = {'User-Agent': UA.random}'''
hdr = {'User-Agent': 'Mozilla/5.0'}

base_url = 'https://www.delcampe.net'

def get_html(url):
    
    html_content = ''
    try:
        page = req.get(url, headers=hdr)
        html_content = BeautifulSoup(page.content, "lxml")
    except: 
        pass
    
    return html_content

def get_details(url,selection,category,subcategory):
    
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
        stamp['raw_text'] = raw_text.replace('"',"'")
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
    
    stamp['base_category']=selection
    stamp['category']=category
    stamp['subcategory']=subcategory
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
'''
def file_names(stamp):
    file_name = []
    rand_string = "RAND_"+str(randint(0,100000000))
    file_name = [rand_string+"-" + str(i) + ".png" for i in range(len(stamp['image_urls']))]
    return(file_name)

def query_for_previous(stamp):
    # CHECKING IF Stamp IN DB
    os.chdir("/Volumes/Stamps/")
    conn1 = sqlite3.connect('Reference_data.db')
    c = conn1.cursor()
    col_nm = 'url'
    col_nm2 = 'raw_text'
    unique = stamp['url']
    unique2 = stamp['raw_text']
    c.execute('SELECT * FROM delecamp WHERE {cn} == "{un}" AND {cn2} == "{un2}"'.\
                format(cn=col_nm, cn2=col_nm2, un=unique, un2=unique2))
    all_rows = c.fetchall()
    print(all_rows)
    conn1.close()
    price_update=[]
    price_update.append((stamp['url'],
    stamp['raw_text'],
    stamp['scrape_date'], 
    stamp['price'], 
    stamp['currency']))
    
    if len(all_rows) > 0:
        print ("This is in the database already")
        sleep(randint(25,55))
        next_step= 'continue'
        pass
    else:
        os.chdir("/Volumes/Stamps/")
        if stamp['price']!=None:
        	conn2 = sqlite3.connect('Reference_data.db')
        	c2 = conn2.cursor()
        	c2.executemany("""INSERT INTO price_list (url, raw_text, scrape_date, price, currency) VALUES(?,?,?,?,?)""", price_update)
        	conn2.commit()
        	conn2.close()
        next_step='pass'
    return(next_step)

def db_update_image_download(stamp):  
    directory = "/Volumes/Stamps/stamps/delecamp/" + str(datetime.datetime.today().strftime('%Y-%m-%d')) +"/"
    image_paths = []
    file_name = file_names(stamp)
    image_paths = [directory + file_name[i] for i in range(len(file_name))]
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    for item in range(0,len(file_name)):
        print (stamp['image_urls'][item])
        try:
            imgRequest1=req.get(stamp['image_urls'][item],headers=hdr, timeout=120, stream=True)
        except:
            print ("waiting...")
            sleep(randint(3000,6000))
            print ("...")
            imgRequest1=req.get(stamp['image_urls'][item], headers=hdr, timeout=120, stream=True)
        if imgRequest1.status_code==200:
            with open(file_name[item],'wb') as localFile:
                imgRequest1.raw.decode_content = True
                shutil.copyfileobj(imgRequest1.raw, localFile)
                sleep(randint(25,40))
    stamp['image_paths']=", ".join(image_paths)
    database_update =[]
    # PUTTING NEW STAMPS IN DB
    database_update.append((
        stamp['url'],
        stamp['raw_text'],
        stamp['title'],
        stamp['base_category'],
        stamp['category'],
        stamp['subcategory'],
        stamp['scrape_date'],
        stamp['image_paths']))
    os.chdir("/Volumes/Stamps/")
    conn = sqlite3.connect('Reference_data.db')
    conn.text_factory = str
    cur = conn.cursor()
    cur.executemany("""INSERT INTO delecamp ('url','raw_text', 'title', 'base_category','category', 'subcategory',
    'scrape_date','image_paths') 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", database_update)
    conn.commit()
    conn.close()
    print ("++++++++++++")
    sleep(randint(35,120)) 

count = 0
connectTor()
'''
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
        print(subcategory)
        choice = input('Do you want to scrape this?')
        if choice =='Y':
            pass
        else:
            continue
        page_url = subcategory
        while(page_url):
            page_items, page_url = get_page_items(page_url)
            for page_item in page_items:
                '''count += 1
                if count > randint(100, 256):
                    print('Sleeping...')
                    sleep(randint(600, 4000))
                    hdr['User-Agent'] = UA.random
                    renew_tor()
                    connectTor()
                    count = 0
                else:
                    pass'''
                stamp = get_details(page_item, selection, category, subcategory)
                '''if stamp['price']==None and stamp['raw_text']==None and stamp['title']==None:
                	sleep(randint(800,2000))
                	continue
                else:
                    pass
                next_step = query_for_previous(stamp)
                if next_step == 'continue':
                    print('Only updating price')
                    continue
                elif next_step == 'pass':
                    print('Inserting the item')
                    pass
                else:
                    break
                db_update_image_download(stamp)'''
print('Scrape Complete')