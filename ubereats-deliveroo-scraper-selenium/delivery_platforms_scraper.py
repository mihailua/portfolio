#!/usr/bin/env python3
from selenium import webdriver
from selenium.common.exceptions import InvalidSelectorException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import time as tm
from datetime import datetime, time, timedelta
import os
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
today = datetime.now()
now = datetime.now().time()

start_time1 = time(22, 0, 0)
end_time1 = time(23, 59, 59)
start_time2 = time(0, 0, 0)
end_time2 = time(12, 00, 00)

#if not ((start_time1 <= now <= end_time1) or (start_time2 <= now <= end_time2)):
#   raise Exception("The current time is not between 10 PM and 11 am.")

if (start_time2 <= now <= end_time2):
    today = today -timedelta(1)

timeperiod_conversion = {'Today':today.strftime("%Y-%m-%d (%A)"), 'Yesterday':(today-timedelta(1)).strftime("%Y-%m-%d (%A)"), '2 days ago':(today-timedelta(2)).strftime("%Y-%m-%d (%A)"), '3 days ago':(today-timedelta(3)).strftime("%Y-%m-%d (%A)"), '4 days ago':(today-timedelta(4)).strftime("%Y-%m-%d (%A)"), '5 days ago':(today-timedelta(5)).strftime("%Y-%m-%d (%A)"), '6 days ago':(today-timedelta(6)).strftime("%Y-%m-%d (%A)"), 'Last week':((today-timedelta(14)).strftime("%Y-%m-%d")+' to '+(today-timedelta(7)).strftime("%Y-%m-%d")), '2 weeks ago':((today-timedelta(21)).strftime("%Y-%m-%d")+' to '+(today-timedelta(14)).strftime("%Y-%m-%d"))}

negative = "M1.54053 9H8.91063L11.9998 0.890976L15.0889 9H22.459L17.2254 14.0995L19.3545 21.5514L11.9998 17.1644L4.64508 21.5514L6.7742 14.0995L1.54053 9ZM6.45904 11L9.02537 13.5005L7.95449 17.2486L11.9998 14.8356L16.0451 17.2486L14.9742 13.5005L17.5405 11H13.7106L11.9998 6.50903L10.2889 11H6.45904Z"
positive = "M12 1L9 9H2L7 14.0001L5 21L12 17.0001L19 21L17 14.0001L22 9H15L12 1Z"

print("https://deliveroo.co.uk/menu/Town/Location/Name-of-Store?")
website = input("Please paste the desired location deliveroo url as per syntax shown above (press Enter for Wingstop): ")

if website == "":
    website = 'https://deliveroo.co.uk/menu/London/whitechapel-editions-site/wingstop-editions-whi/'


options = Options()
options.add_argument('--disable-gpu')

driver = webdriver.Chrome(options=options)

driver.get(website)

tm.sleep(7)
driver.save_screenshot('debug.png')
try:
    cookies = driver.find_element(By.XPATH, '//div[@id="onetrust-button-group"]/button[2]')

    cookies.click()

    tm.sleep(1)
    no_loc = driver.find_element(By.XPATH,
                                 '//button[@class="ccl-4704108cacc54616 ccl-4f99b5950ce94015 ccl-8939b7e2297ccfd5"]')

    no_loc.click()

    tm.sleep(1)

except NoSuchElementException:
    print('')

Store_name = driver.find_element(By.XPATH,'//h1').text
print("Scraping "+Store_name+" :)")
populars = driver.find_elements(By.XPATH,'//div[@class="MenuItemCard-1e17f722e482e103" and .//span[@class="ccl-649204f2a8e630fd ccl-6f43f9bb8ff2d712 ccl-32ec9a3197735a65 ccl-89c73b0906008f40"]]//p')
populars = [item.text for item in populars]


reviews = driver.find_element(By.XPATH,'//div[@class="MenuHeader-45db0548af3525e1 ccl-885f4456fb02b69c ccl-0902d2cf2567c221 ccl-d799b1662a7b52b8"]/div[5]/div/span/button')

reviews.click()

tm.sleep(2)

reviews_sort = driver.find_element(By.XPATH,'//div[@class="PopoverManager-e373249d3714e14a"]/span/button')

reviews_sort.click()

tm.sleep(2)

most_recent_sort = driver.find_element(By.XPATH,'//span[@class="ccl-649204f2a8e630fd ccl-a396bc55704a9c8a ccl-40ad99f7b47f3781 ccl-ea9144c387bfb5b8 ccl-2c8747592795e0b6 ccl-1a9489aff90b6be4 ccl-8823d35f572eda4a" and text()="Most recent"]')

most_recent_sort.click()

tm.sleep(3)

#path to all 5 stars of todays reviews = //span[@class="ReviewBody-e030257d2fca1dbd" and span[2][text()="Today"]]/span[1]
#path to all values of all today's stars = //span[@class="ReviewBody-e030257d2fca1dbd" and span[2][text()="Today"]]/span[1]//@d
#the len of the above devided by 5 gives number of reviews, so counting how many of them are ...1Z and deviding by that number = average scoree of the day
while len(driver.find_elements(By.XPATH, '//span[@class="ReviewBody-e030257d2fca1dbd" and span[2][text()="3 weeks ago"]]')) == 0:
    load_more_button = driver.find_element(By.XPATH,'//button[@class="ccl-388f3fb1d79d6a36 ccl-9ed29b91bb2d9d02 ccl-59eced23a4d9e077 ccl-7be8185d0a980278"]/span')
    load_more_button.click()
    tm.sleep(2)

reviews_daily = pd.DataFrame()
reviews_weekly = pd.DataFrame()
for timeperiod in ['Today', 'Yesterday', '2 days ago', '3 days ago', '4 days ago', '5 days ago', '6 days ago', 'Last week', '2 weeks ago']:
    #reviews with promotion
    rating_with_promo = driver.find_elements(By.XPATH,
                                  f'//span[@class="ReviewBody-e030257d2fca1dbd" and span[2][text()=\"{timeperiod}\"]]//*[local-name() = "svg"]/*[local-name() = "path"]')
    rating_with_promo = [rate.get_attribute('d') for rate in rating_with_promo]
    rating_with_promo = [item for item in rating_with_promo if item == positive or item == negative]
    rating_with_promo = [1 if value==positive else 0 for value in rating_with_promo]

    rating_without = driver.find_elements(By.XPATH,
                                             f'//div[@class="ReviewBody-0f872b327d6312b2" and .//span[2][text()=\"{timeperiod}\"] and ./div/div/div[not(p)]]//*[local-name() = "svg"]/*[local-name() = "path"] | //div[@class="ReviewBody-0f872b327d6312b2" and .//span[2][text()=\"{timeperiod}\"] and .//p/span[1][not(contains(normalize-space(.),"#"))]]//*[local-name() = "svg"]/*[local-name() = "path"]')
    rating_without = [rate.get_attribute('d') for rate in rating_without]
    rating_without = [item for item in rating_without if item == positive or item == negative]
    rating_without = [1 if value == positive else 0 for value in rating_without]


    goodpoints = driver.find_elements(By.XPATH,f'//div[@class="ccl-955fe0ab28803310" and .//span[text()=\"{timeperiod}\"] and .//@style="background: rgb(228, 242, 212); color: rgb(77, 124, 27);"]//span[@class="ccl-5512b5f3ef660fd9"]')
    goodpoints = [point.text for point in goodpoints]
    goodpoints = {point:goodpoints.count(point) for point in set(goodpoints)}
    goodpoints = dict(sorted(goodpoints.items(), key=lambda item: item[1], reverse=True))

    badpoints = driver.find_elements(By.XPATH,f'//div[@class="ccl-955fe0ab28803310" and .//span[text()=\"{timeperiod}\"] and .//@style="background: rgb(255, 246, 245); color: rgb(204, 58, 47);"]//span[@class="ccl-5512b5f3ef660fd9"]')
    badpoints = [point.text for point in badpoints]
    badpoints = {point: badpoints.count(point) for point in set(badpoints)}
    badpoints = dict(sorted(badpoints.items(), key=lambda item: item[1], reverse=True))


    if timeperiod != "Today":
        populars = []
    date = timeperiod_conversion[timeperiod]
    record_key = {'Date': date,'AVG_score': round(5*float(sum(rating_with_promo))/float(len(rating_with_promo)),2), 'Num_of_reviews': len(rating_with_promo)/5, 'AVG_score_without_promo': round(5*float(sum(rating_without))/float(len(rating_without)),2),
                'Numb_of_reviews_without_promo': len(rating_without)/5, 'Good_points': goodpoints,'Bad points':badpoints,'Popular_items':populars}
    if "week" not in timeperiod:
        reviews_daily = pd.concat([reviews_daily, pd.DataFrame([record_key])], ignore_index=True)
    else:
        reviews_weekly = pd.concat([reviews_weekly, pd.DataFrame([record_key])], ignore_index=True)

reviews_daily = reviews_daily[::-1].reset_index(drop=True)
reviews_weekly= reviews_weekly[::-1].reset_index(drop=True)

# Check if file exists
if not os.path.exists(current_dir+'/'+'records_daily.xlsx'):
    empty_df=pd.DataFrame()
    empty_df.to_excel(current_dir+'/'+'records_daily.xlsx', index=False, sheet_name=Store_name)

# Adding or editing sheets
with pd.ExcelWriter(current_dir+'/'+'records_daily.xlsx', engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
    if Store_name in writer.book.sheetnames:
        df = pd.read_excel(current_dir+'/'+'records_daily.xlsx', sheet_name=Store_name)
        if len(df) != 0:
            dates = df["Date"].unique()
        else:
            dates = []
        reviews_daily = reviews_daily[~reviews_daily['Date'].isin(dates)]
        reviews_daily = pd.concat([df, reviews_daily], ignore_index=True)
    else:
        empty_df = pd.DataFrame()
        empty_df.to_excel(current_dir + '/' + 'records_daily.xlsx', index=False, sheet_name=Store_name)
    reviews_daily.to_excel(writer, sheet_name=Store_name, index=False)

if today.weekday() != 2 :
    print('!THE WEEKLY RECORDS WOULD ONLY BE UPDATED ON A SUNDAY!')

else:
    if not os.path.exists(current_dir + '/' + 'records_weekly.xlsx'):
        empty_df = pd.DataFrame()
        empty_df.to_excel(current_dir + '/' + 'records_weekly.xlsx', index=False, sheet_name=Store_name)

    # Adding or editing sheets
    with pd.ExcelWriter(current_dir + '/' + 'records_weekly.xlsx', engine="openpyxl", mode="a",
                        if_sheet_exists="replace") as writer:
        if Store_name in writer.book.sheetnames:
            df = pd.read_excel(current_dir + '/' + 'records_weekly.xlsx', sheet_name=Store_name)
            if len(df)!=0:
                dates = df["Date"].unique()
            else:
                dates=[]
            reviews_weekly = reviews_weekly[~reviews_weekly['Date'].isin(dates)]
            reviews_weekly = pd.concat([df, reviews_weekly], ignore_index=True)
        else:
            empty_df = pd.DataFrame()
            empty_df.to_excel(current_dir + '/' + 'records_weekly.xlsx', index=False, sheet_name=Store_name)
        reviews_weekly.to_excel(writer, sheet_name=Store_name, index=False)

print("Success :p")

uberyesorno = input("Uber? (y/n)")[0].casefold()
if uberyesorno =="y":
    print("https://www.ubereats.com/gb/store/name/kakie-to-numbers")
    website = input("Please paste the desired location UberEats url as per syntax shown above (press Enter for PizzaHut): ")

    if website == "":
        website = 'https://www.ubereats.com/store/pizza-hut-express-westfield-stratford-city/2g8q6JghW8KiT2gvJI0jFw'

    driver = webdriver.Chrome()

    driver.get(website)

    tm.sleep(5)

    try:
        promo = driver.find_element(By.XPATH, '//button[@aria-label="Close" and @data-testid="close-button')
        promo.click()
        tm.sleep(1)
    except InvalidSelectorException:
        print('')
    Store_name = driver.find_element(By.XPATH, '//h1').text
    uberstats = driver.find_elements(By.XPATH,'//div[./div/span[@data-testid="rich-text"] and ./div/*[local-name() = "svg"]]/div[1]/span | //div[./div/span[@data-testid="rich-text"] and ./div/*[local-name() = "svg"]]/div[2]/span[3]')

    uberstats = [stat.text for stat in uberstats]
    key = {'Date': today.strftime("%Y-%m-%d (%A)")}
    key.update({uberstats[::2][i].strip():uberstats[1::2][i].strip() for i in range(len(uberstats)//2)})

    if not os.path.exists(current_dir + '/' + 'uber_records.xlsx'):
        empty_df = pd.DataFrame(columns=['Date'])
        empty_df.to_excel(current_dir + '/' + 'uber_records.xlsx', index=False, sheet_name=Store_name)

    # Adding or editing sheets
    with pd.ExcelWriter(current_dir + '/' + 'uber_records.xlsx', engine="openpyxl", mode="a",
                        if_sheet_exists="replace") as writer:
        jopa=pd.DataFrame([key])
        if Store_name in writer.book.sheetnames:
            df = pd.read_excel(current_dir + '/' + 'uber_records.xlsx', sheet_name=Store_name)
            jopa = pd.concat([df, jopa], ignore_index=True)
        else:
            empty_df = pd.DataFrame()
            empty_df.to_excel(current_dir + '/' + 'uber_records.xlsx', index=False, sheet_name=Store_name)
        jopa = jopa.drop_duplicates()
        jopa.to_excel(writer, sheet_name=Store_name, index=False)
        print("Uber data collected")

# load more reviews - button[class='ccl-388f3fb1d79d6a36 ccl-9ed29b91bb2d9d02 ccl-59eced23a4d9e077 ccl-7be8185d0a980278'] span[class='ccl-bc70252bc472695a']

#when len(find_elemenents...)>0 we stop loading more : //span[@class="ReviewBody-e030257d2fca1dbd" and span[2][text()="3 weeks ago"]]
#text of the reviews //div[@class="ReviewBody-0f872b327d6312b2"]//p/span[1]
#all reviews with text but without hashtag //div[@class="ReviewBody-0f872b327d6312b2"]//p/span[1][not(contains(normalize-space(.),'#'))]
#all reviews without text //div[@class="ReviewBody-0f872b327d6312b2"]/div/div/div[not(p)]
#all reviews either without text or without hashtag in text //div[@class="ReviewBody-0f872b327d6312b2"]/div/div/div[not(p)] | //div[@class="ReviewBody-0f872b327d6312b2"]//p/span[1][not(contains(normalize-space(.),'#'))]
#today reviews without text //div[@class="ReviewBody-0f872b327d6312b2" and .//span[2][text()="Today"] and ./div/div/div[not(p)]]
#today reviews with text without hashtag //div[@class="ReviewBody-0f872b327d6312b2" and .//span[2][text()="Today"] and .//p/span[1][not(contains(normalize-space(.),'#'))]]
#today reviews either no text or no hashtag in text //div[@class="ReviewBody-0f872b327d6312b2" and .//span[2][text()="Today"] and ./div/div/div[not(p)]]//*[local-name() = "svg"]/*[local-name() = "path"] | //div[@class="ReviewBody-0f872b327d6312b2" and .//span[2][text()="Today"] and .//p/span[1][not(contains(normalize-space(.),'#'))]]//*[local-name() = "svg"]/*[local-name() = "path"]
#have to takee into account that //path/@d contains emojies as well

#positive points //div[@class='ccl-955fe0ab28803310' and .//span[text()="2 weeks ago"] and .//@style="background: rgb(228, 242, 212); color: rgb(77, 124, 27);"]//span[@class="ccl-5512b5f3ef660fd9"]
#negative points //div[@class='ccl-955fe0ab28803310' and .//span[text()="2 weeks ago"] and .//@style="background: rgb(255, 246, 245); color: rgb(204, 58, 47);"]//span[@class="ccl-5512b5f3ef660fd9"]
# ubereats data //div[@class="al dm a23 am bh" and .//span[3][@class="qz r0 r1 bo c3 bq f0 b1"]]/div[1]/span[1] | //div[@class="al dm a23 am bh"]//span[3][@class="qz r0 r1 bo c3 bq f0 b1"]

