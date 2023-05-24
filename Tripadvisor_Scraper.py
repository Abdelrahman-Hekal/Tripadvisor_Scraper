from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import pandas as pd
import time
import os
import csv
import unidecode
import numpy as np
import undetected_chromedriver as uc

def initialize_bot():

    # Setting up chrome driver for the bot
    #chrome_options  = webdriver.ChromeOptions()
    chrome_options = uc.ChromeOptions()
    #chrome_options.add_argument('--headless')
    #chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    chrome_options.add_argument('--log-level=3')
    #chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument("--start-maximized")
    #chrome_options.add_argument("--disable-blink-features")
    #chrome_options.add_argument("--incognito")
    #chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    #chrome_options.add_argument('--disable-gpu')
    #########################################
    #chrome_options.add_argument("--disable-dev-shm-usage")
    #chrome_options.add_argument("--no-sandbox")
    #chrome_options.add_argument("--disable-impl-side-painting")
    #chrome_options.add_argument("--disable-setuid-sandbox")
    #chrome_options.add_argument("--disable-seccomp-filter-sandbox")
    #chrome_options.add_argument("--disable-breakpad")
    #chrome_options.add_argument("--disable-client-side-phishing-detection")
    #chrome_options.add_argument("--disable-cast")
    #chrome_options.add_argument("--disable-cast-streaming-hw-encoding")
    #chrome_options.add_argument("--disable-cloud-import")
    #chrome_options.add_argument("--disable-popup-blocking")
    #chrome_options.add_argument("--ignore-certificate-errors")
    #chrome_options.add_argument("--disable-session-crashed-bubble")
    #chrome_options.add_argument("--disable-ipv6")
    #chrome_options.add_argument("--allow-http-screen-capture")
    #chrome_options.add_argument("--start-maximized")

    #chrome_options.add_argument("--disable-extensions") 
    #chrome_options.add_argument("--disable-notifications") 
    #chrome_options.add_argument("--disable-infobars") 
    #chrome_options.add_argument("--remote-debugging-port=9222")
    #chrome_options.add_argument('--disable-dev-shm-usaging')
############################################
    chrome_options.page_load_strategy = 'normal'
    PROXY = "20.47.108.204:8888"
    #PROXY = "5.189.184.6:80"
    chrome_options.add_argument('--proxy-server=%s' % PROXY)
    #driver = uc.Chrome(options=chrome_options)
    path = ChromeDriverManager().install()
    driver = webdriver.Chrome(path, options=chrome_options)
    driver.set_page_load_timeout(60)
    driver.maximize_window()
    return driver

def scrape_restaurants(driver, output, links, sponsers):

    # checking scraped restaurants
    df = pd.read_csv(output)
    scraped = np.unique(df['res_url'].values.tolist()).tolist()
    try:
        n = df['res_id'].values.max()
        if n == None:
            n = 0
    except:
        n = 0
        
        
    keys = ["res_id",	"res_name",	"res_sponsor",	"res_review",	"res_type",	"res_price", "res_url",	"res_claim",	"res_loc",	"res_phone",	"res_rate",	"res_food",	"res_service",	"res_value",	"res_atmos",	"com_id",	"com_rate",	"com_title",	"com_content",	"com_pic",	"com_date",	"com_help",	"com_url",	"com_clientname",	"com_clientcom",	"client_level",	"client_start",	"client_age",	"client_gender",	"client_loc",	"client_contribute",	"client_visit",	"client_help",	"client_pic",	"client_5",	"client_4",	"client_3",	"client_2",	"client_1",	"client_url"]

    row = {}
    for l, link in enumerate(links):
        try:
            if link in scraped: continue
            for key in keys:
                row[key] = 'N/A'

            driver.get(link)
            #time.sleep(1e6)
            row["res_sponsor"] = sponsers[l]
            #name
            name = wait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.HjBfq"))).text
            
            row['res_name'] = name
            n += 1
            print(f'Scraping Details For Restaurant {n}: {name} ...')           
            # id
            row['res_id'] = n

            #reviews
            try:
                nrev = wait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.AfQtZ"))).text.split(' ')[0].replace(',', '')
                row['res_review'] = int(nrev) 
            except:
                pass
          
            # res page
            row['res_url'] = link
            #type
            try:
                res_type = ''
                elems = wait(driver, 1).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.dlMOJ")))[1:]
                for elem in elems:
                    res_type += elem.text + ', '

                if len(res_type) > 0:
                    row['res_type'] = res_type[:-2]
            except:
                pass
         
            #price
            try:
                price = wait(driver, 1).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.dlMOJ")))[0].text
                if price.find('-') == -1:
                    count = price.count('$')
                else:
                    count1 = price[:price.find('-')].count('$')
                    count2 = price[price.find('-')+1:].count('$')
                    count = str(count1) + '-' + str(count2)

                row['res_price'] = count
            except:
                pass

            #claim
            try:
                text = wait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.DkEDW"))).text.lower()
                if 'unclaimed' in text:
                    row['res_claim'] = 0
                else:
                    row['res_claim'] = 1          
            except:
                row['res_claim'] = 0
                
            #address
            try:
                add = wait(driver, 1).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.AYHFM")))[1].text
                row['res_loc'] = add    
            except:
                pass
            
            #tel
            try:
                tel = wait(driver, 1).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.BMQDV._F.G-.wSSLS.SwZTJ")))[1].text
                row['res_phone'] = tel 
            except:
                pass 
            
            #overall rating
            try:
                rating = wait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.ZDEqb"))).text.strip()
                row['res_rate'] = rating 
            except:
                pass
            
            #food rating
            try:
                span = wait(driver, 1).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.vzATR")))[0]
                text = wait(span, 1).until(EC.presence_of_element_located((By.TAG_NAME, "span"))).get_attribute('class').split('_')[-1].strip()
                food_rating = text[0] + '.' + text[1:]
                row['res_food'] = food_rating 
            except:
                pass
            
            #service rating
            try:
                span = wait(driver, 1).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.vzATR")))[1]
                text = wait(span, 1).until(EC.presence_of_element_located((By.TAG_NAME, "span"))).get_attribute('class').split('_')[-1].strip()
                ser_rating = text[0] + '.' + text[1:]
                row['res_service'] = ser_rating     
            except:
                pass
            
            #value rating
            try:
                span = wait(driver, 1).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.vzATR")))[2]
                text = wait(span, 1).until(EC.presence_of_element_located((By.TAG_NAME, "span"))).get_attribute('class').split('_')[-1].strip()
                val_rating = text[0] + '.' + text[1:]
                row['res_value'] = val_rating  
            except:
                pass
            
            try:
                #atmos rating
                span = wait(driver, 1).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.vzATR")))[3]
                text = wait(span, 1).until(EC.presence_of_element_located((By.TAG_NAME, "span"))).get_attribute('class').split('_')[-1].strip()
                atm_rating = text[0] + '.' + text[1:]
                row['res_atmos'] = atm_rating
            except:
                pass

            # nrevs
            try:
                text = wait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//div[@class='item' and @data-value='en']"))).text
                res_nrev = int(text[text.find('(')+1:text.find(')')].replace(',', ''))
            except:
                res_nrev = 0

            if res_nrev == 0:
                output_row(output, row)
            else:
                com_id = 0
                done = False
                # scraping res reviews
                while True:
                    if done: break
                    revs = wait(driver, 1).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.review-container")))
                    for rev in revs:
                        rev_keys = ["com_id",	"com_rate",	"com_title",	"com_content",	"com_pic",	"com_date",	"com_help",	"com_url",	"com_clientname",	"com_clientcom",	"client_level",	"client_start",	"client_age",	"client_gender",	"client_loc",	"client_contribute",	"client_visit",	"client_help",	"client_pic",	"client_5",	"client_4",	"client_3",	"client_2",	"client_1",	"client_url"]
                        for key in rev_keys:
                            row[key] = 'N/A'
                        com_id += 1
                        row['com_id'] = com_id
                        #user rating
                        try:
                            div = wait(rev, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ui_column.is-9")))
                            text = wait(div, 1).until(EC.presence_of_all_elements_located((By.TAG_NAME, "span")))[0].get_attribute('class').split('_')[-1].strip()
                            rating = text[0] + '.' + text[1:]
                            row['com_rate'] = rating    
                        except:
                            pass
                    
                        #user title
                        try:
                            title = wait(rev, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.title"))).text
                            row['com_title'] = title  
                        except:
                            pass
                    
                        #user link
                        try:
                            url = wait(rev, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.title"))).get_attribute('href')
                            row['com_url'] = url
                        except:
                            pass

                        # user nrevs
                        try:
                            div = wait(rev, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.prw_rup.prw_reviews_text_summary_hsx")))
                            button = wait(div, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.taLnk.ulBlueLinks")))
                            if button.text == 'Show less':
                                driver.execute_script("arguments[0].click();", button)
                            time.sleep(1)
                        except:
                            pass

                        try:
                            nrev = wait(rev, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.badgeText"))).text.split(' ')[0].replace(',', '')
                            row['com_clientcom'] = nrev
                        except:
                            pass

                        #user content
                        p = wait(rev, 1).until(EC.presence_of_element_located((By.TAG_NAME, "p")))
                        try:
                            button = wait(p, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.taLnk.ulBlueLinks")))
                            if button.text == 'More':
                                driver.execute_script("arguments[0].click();", button)
                            time.sleep(1)
                            p = wait(rev, 1).until(EC.presence_of_element_located((By.TAG_NAME, "p")))
                        except:
                            pass
                        row['com_content'] = p.text

                        # images
                        try:
                            imgs = wait(rev, 1).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.photoContainer")))
                            row['com_pic'] = len(imgs)
                        except:
                            row['com_pic'] = 0

                        # date
                        try:
                            date = wait(rev, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.ratingDate"))).get_attribute('title').strip()
                            row['com_date'] = date     
                        except:
                            pass
                    
                        # helpful
                        try:
                            thanks = wait(rev, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.numHelp"))).text.strip()
                            if len(thanks) > 0:
                                row['com_help'] = thanks
                            else:
                                row['com_help'] = 'N/A'
                        except:
                            pass

                        # user name
                        try:
                            name = wait(rev, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.info_text.pointer_cursor"))).text.split('\n')[0]
                            row['com_clientname'] = name   
                        except:
                            pass
                     
                        # getting user details
                        try:
                            div = wait(rev, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.avatarWrapper")))
                            button = wait(div, 1).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
                            driver.execute_script("arguments[0].click();", button)
                            popup = wait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.ui_overlay.ui_popover.arrow_left")))
                        except:
                            pass

                        # user level
                        try:
                            div = wait(popup, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.badgeinfo")))
                            level = wait(div, 1).until(EC.presence_of_element_located((By.TAG_NAME, "span"))).text
                            row['client_level'] = level
                        except:
                            pass                    
                        
                        # user register date
                        try:
                            ul = wait(popup, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.memberdescriptionReviewEnhancements")))
                            date = wait(ul, 1).until(EC.presence_of_all_elements_located((By.TAG_NAME, "li")))[0].text.split(' ')[-1]
                            row['client_start'] = int(date)
                        except:
                            pass                                                     
                        # user age, gender and loc
                        try:
                            ul = wait(popup, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.memberdescriptionReviewEnhancements")))
                            lis = wait(ul, 1).until(EC.presence_of_all_elements_located((By.TAG_NAME, "li")))
                            for li in lis:
                                content = li.text
                                if content.find('-') != -1:
                                    row['client_age'] = content.split(' ')[0]
                                if 'man ' in content.lower():
                                    row['client_gender'] = 'Man'
                                if 'woman ' in content.lower():
                                    row['client_gender'] = 'Woman'

                                if content.find('from') != -1:
                                    words = content.split(' ')
                                    ind = words.index('from') 
                                    row['client_loc'] = ' '.join(words[ind+1:]).title()
                                if content.find('From') != -1:
                                    words = content.split(' ')
                                    ind = words.index('From') 
                                    row['client_loc'] = ' '.join(words[ind+1:]).title()
                        except:
                            pass                
                            
                        # user contrib, visits, helpful and votes
                        try:
                            ul = wait(popup, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.countsReviewEnhancements")))
                            lis = wait(ul, 1).until(EC.presence_of_all_elements_located((By.TAG_NAME, "li")))
                            for li in lis:
                                if 'Contribution' in li.text:
                                    row['client_contribute'] = li.text.split(' ')[0].replace(',', '')                           
                                elif 'Cities visited' in li.text or 'City visited' in li.text:
                                    row['client_visit'] = li.text.split(' ')[0].replace(',', '')                              
                                elif 'Helpful vote' in li.text:
                                    row['client_help'] = li.text.split(' ')[0].replace(',', '')                              
                                elif 'Photo' in li.text:
                                    row['client_pic'] = li.text.split(' ')[0].replace(',', '')  
                        except:
                            pass

                        # user url
                        try:
                            url = wait(popup, 1).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))[0].get_attribute('href')
                            row['client_url'] = url 
                        except:
                            pass                    
                        
                        # user url
                        try:
                            menu = wait(popup, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.wrap.container.histogramReviewEnhancements")))
                            divs = wait(menu, 1).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.chartRowReviewEnhancements")))
                            for div in divs:
                                if 'Excellent' in div.text:
                                    row['client_5'] = div.text.split('\n')[-1].replace(',', '')                              
                                elif 'Very good' in div.text:
                                    row['client_4'] = div.text.split('\n')[-1].replace(',', '')                              
                                elif 'Average' in div.text:
                                    row['client_3'] = div.text.split('\n')[-1].replace(',', '')                              
                                elif 'Poor' in div.text:
                                    row['client_2'] = div.text.split('\n')[-1].replace(',', '')                              
                                elif 'Terrible' in div.text:
                                    row['client_1'] = div.text.split('\n')[-1].replace(',', '')  
                        except:
                            pass

                        #closing user details window
                        try:
                            button = wait(popup, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ui_close_x")))
                            driver.execute_script("arguments[0].click();", button)
                            time.sleep(1)
                        except:
                            pass

                        # adding the scraped data to the final output
                        #data.append(row.copy())
                        output_row(output, row)
                        print(f'Review {com_id}/{res_nrev} is scraped ...')

                    # checking if there is further pages
                    try:
                        button = wait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.nav.next.ui_button.primary.disabled")))
                        if com_id < res_nrev:
                            print(f'Warning: Site is showing {res_nrev} reviews while {com_id} reviews were scraped!')
                        done = True
                        break
                    except:
                        try:
                            # getting the current page number
                            page_div = wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.pageNumbers")))
                            num1 = wait(page_div, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[class*='current']"))).text
                            # moving to the next reviews page
                            button = wait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//a[@class='nav next ui_button primary']")))
                            driver.execute_script("arguments[0].click();", button)
                            time.sleep(5)
                            page_div = wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.pageNumbers")))
                            num2 = wait(page_div, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[class*='current']"))).text
                            if num1 == num2:
                                while True:
                                    print('Reviews page did not loaded correctly, retrying ...')
                                    driver.refresh()
                                    # moving to the next page
                                    button = wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.nav.next.ui_button.primary")))
                                    driver.execute_script("arguments[0].click();", button)
                                    time.sleep(5)
                                    page_div = wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.pageNumbers")))
                                    num2 = wait(page_div, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[class*='current']"))).text
                                    if num1 != num2:
                                        break
                        except:
                            if com_id < res_nrev:
                                print(f'Warning: Site is showing {res_nrev} reviews while {com_id} reviews were scraped!')
                            done = True
                            break
        except Exception as err:
            print('Warning: the following error ocurred:')
            print(str(err))
            driver.refresh()
            time.sleep(3)
            continue

    driver.close()

def remove_output(output, res):

    df = pd.read_csv(output)
    inds = df[df['res_name'] == res].index
    df.drop(inds, inplace= True)
    df.to_csv(output, encoding='UTF-8', index= False)
   
def initialize_output():

    path = os.getcwd()
    files = os.listdir(path)
    for sheet in files:
        if sheet == 'NY_Res_Scraped_Data.csv':
            output = path + "\\" + sheet
            return output

    header = ["res_id",	"res_name",	"res_sponsor",	"res_review",	"res_type",	"res_price", "res_url",	"res_claim",	"res_loc",	"res_phone",	"res_rate",	"res_food",	"res_service",	"res_value",	"res_atmos",	"com_id",	"com_rate",	"com_title",	"com_content",	"com_pic",	"com_date",	"com_help",	"com_url",	"com_clientname",	"com_clientcom",	"client_level",	"client_start",	"client_age",	"client_gender",	"client_loc",	"client_contribute",	"client_visit",	"client_help",	"client_pic",	"client_5",	"client_4",	"client_3",	"client_2",	"client_1",	"client_url"]

    #filename = 'NY_Res_Scraped_Data_{}.csv'.format(datetime.now().strftime("%d_%m_%Y_%H_%M"))
    filename = 'NY_Res_Scraped_Data.csv'

    
    if path.find('/') != -1:
        output = path + "/" + filename
    else:
        output = path + "\\" + filename

    with open(output, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

    return output

def output_row(output, row):

    keys = ["res_id",	"res_name",	"res_sponsor",	"res_review",	"res_type",	"res_price", "res_url",	"res_claim",	"res_loc",	"res_phone",	"res_rate",	"res_food",	"res_service",	"res_value",	"res_atmos",	"com_id",	"com_rate",	"com_title",	"com_content",	"com_pic",	"com_date",	"com_help",	"com_url",	"com_clientname",	"com_clientcom",	"client_level",	"client_start",	"client_age",	"client_gender",	"client_loc",	"client_contribute",	"client_visit",	"client_help",	"client_pic",	"client_5",	"client_4",	"client_3",	"client_2",	"client_1",	"client_url"]

    line = []
    for key in keys:
        line.append(unidecode.unidecode(str(row[key])))

    with open(output, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(line)

def clear_screen():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
  
    # for mac and linux
    else:
        _ = os.system('clear')

def get_res_links(driver):

    # checking if links file already exists
    path = os.getcwd()
    files = os.listdir(path)
    for sheet in files:
        if sheet == 'NY_Res_Links.csv':
            df = pd.read_csv(path + '\\' + sheet)
            return df.link, df.sponser

    # building the links database if doesn't exist
    with open(path + '\\NY_Res_Links.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['link', 'sponser'])

    url = 'https://www.tripadvisor.com/Restaurants-g60763-New_York_City_New_York.html'
    driver.get(url)
    nres = wait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.EaRai.Gh"))).text.split(' ')[0]
    nres = int(nres)
    n = 0
    while True:
        div = wait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.YtrWs")))
        restaurants = wait(div, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.YHnoF.Gi.o")))

        for res in restaurants:
            n += 1
            # sponser info
            try:
                wait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.RDKqq")))
                sponser = 1
            except:
                sponser = 0

            # res page
            link = wait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.Lwqic.Cj.b"))).get_attribute('href')

            with open(path + '\\NY_Res_Links.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([link, sponser])

            print(f'link is scraped for res {n}/{nres} ...')
        # moving to the next res page
        try:
            button = wait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.nav.next.rndBtn.ui_button.primary.taLnk")))
            driver.execute_script("arguments[0].click();", button)
            time.sleep(5)
        except:
            if n < nres:
                print(f'Warning: Site is showing {nres} restaurants while {n} restaurants were scraped!')
            break

    df = pd.read_csv(path + '\\NY_Res_Links.csv')
    return df.link, df.sponser

def merge_data():

    path = os.getcwd() + '\\output'
    if not os.path.isdir(path):
        print('No sub batches to merge!')
        return

    df = pd.DataFrame()
    sheets = os.listdir(path)
    for sheet in sheets:
        if 'NY_Res_Scraped_Data' in sheet and sheet[-4:] == '.csv':
            df_sheet = pd.read_csv(path +'\\'+sheet)
            df = df.append(df_sheet.copy())
            #print(df.shape[0])

    print(f'data size before cleaning: {df.shape[0]}')
    restaurants = df['res_url'].unique()
    nres = len(restaurants)
    print(f"Total number of restaurants before cleaning: {nres}")
    df.drop_duplicates(inplace=True)
    df.fillna('N/A', inplace=True)
    df['res_price'] = df['res_price'].apply(lambda x: x.replace('-', '_'))
    df = df.reset_index(drop=True)
    restaurants = df['res_url'].unique()
    nres = len(restaurants)
    print(f'data size after cleaning: {df.shape[0]}')
    print(f"Total number of restaurants after cleaning: {nres}")

    # setting the res_id
    i = 0
    for res in restaurants:
        i += 1
        mask = df[df['res_url'] == res]
        inds = mask.index
        df.loc[inds, 'res_id'] = i
        #res_nrev = mask.loc[inds[0], 'res_review']
        #rev_scraped = mask.shape[0]
        #if rev_scraped < res_nrev/2:
        #    print(f"Incomplete reviews for res {mask.loc[inds[0], 'res_name']}")
        #    df.drop(inds, inplace=True)
        #print(res)

    #df.to_excel('NY_Res_Scraped_Data.xlsx', encoding='UTF-8', index= False)
    df.to_csv('NY_Res_Scraped_Data.csv', encoding='UTF-8', index= False)


# main program      
if __name__ == '__main__':

    driver = initialize_bot()
    clear_screen()
    links, sponsers = get_res_links(driver)
    output = initialize_output()
    scrape_restaurants(driver, output, links, sponsers)
    merge_data()