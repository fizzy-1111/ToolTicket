# # Imports stealth
# from selenium import webdriver
# import time

# # Instantiate a Chrome webdriver instance
# driver = webdriver.Chrome()  

# # Navigate to YouTube homepage
# driver.get('https://www.youtube.com/')

# # Wait for the page to load
# time.sleep(5)

# # Find the first video element on the page and click on it
# video = driver.find_element("xpath",'//*[@id="video-title-link"]/yt-formatted-string')
# video.click()

# # Wait for the video to load
# time.sleep(5)
import requests
import random
from bs4 import BeautifulSoup
# # Close the webdriver
# driver.close()
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium import webdriver 
from selenium.webdriver.common.by import By 
import chromedriver_autoinstaller 
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys 
from fake_useragent import UserAgent
from selenium_stealth import stealth
from pypasser import reCaptchaV3
import seleniumLib
import time 
import json

def Booking(session):
# Extract the access token from the login response
    HotShow_url = "https://api.ticketbox.vn/v1.0/events/top-banner"
    hotshow_res = session.get(HotShow_url)
    hotshow_data = hotshow_res.json()["data"]
    for show in hotshow_data:
        if "Meen Ping" in show["name"]:
            show_id = show["id"]
            chosenShowUrl=show["fullUrl"]
            break

    # Print the ID of the
    print(chosenShowUrl)
    response = session.get(chosenShowUrl)
    soup = BeautifulSoup(response.content, "html.parser")
    script_tag = soup.find_all("script", type="text/javascript")
    pageViewEventDetail_script = next((script for script in script_tag if "pageViewEventDetail" in script.text), None)
    bookingUrl = next((line for line in pageViewEventDetail_script.text.splitlines() if "bookingUrl" in line), None)


    # Print the bookingUrl value or a message if it is not found
    if bookingUrl:
        start_index = bookingUrl.find("/")  # find the index of the first slash
        end_index = bookingUrl.rfind("'")  # find the index of the last slash
        url_string = bookingUrl[start_index:end_index]
        print(url_string)
    else:
        print("Booking URL not found.")
    completeBookingUrl = "https://ticketbox.vn" + url_string
    return completeBookingUrl, url_string
def booked_seatsPosition(seat):
    if seat['status'] == 1 and seat['orderExpireDate'] == None:
        return False
    else:
        return True
def find_seats_in_json(status, order_expire_date, order_id, data):
    results = []
    for section in data['sections']:
        for row in section['rows']:
            seats = row['seats']
            seats = sorted(row['seats'], key=lambda seat: int(seat['name']))
            for i, seat in enumerate(seats):
                if booked_seatsPosition(seat)==False:
                    seat['status'] = 3
                    if i > 1 and booked_seatsPosition(seats[i-1])==False and booked_seatsPosition(seats[i-2])==True:
                        # the seat on the left is already booked or not available
                        seat['status'] = 1
                        continue                                    
                    if i < len(seats)-2 and booked_seatsPosition(seats[i+1])==False and booked_seatsPosition(seats[i+2])==True:
                        # the seat on the right is already booked or not available
                        seat['status'] = 1
                        continue
                    if i==1 and booked_seatsPosition(seats[i-1])==False:
                        seat['status'] = 1
                        continue
                    if i==len(seats)-2 and booked_seatsPosition(seats[i+1])==False: 
                        seat['status'] = 1
                        continue
                    if i==0 and booked_seatsPosition(seats[i+1])==False and booked_seatsPosition(seats[i+2])==True:
                        seat['status'] = 1
                        continue
                    if i==len(seats)-1 and booked_seatsPosition(seats[i-1])==False and booked_seatsPosition(seats[i-2])==True:  
                        seat['status'] = 1
                        continue
                    if(len(results)>4):
                        return results
                    results.append(seat)
                    button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'circle[id="seat-{}"]'.format(seat['id']))))
                    button.click()
                    seat['status'] = 3
                    time.sleep(random.uniform(0.5, 2))
                    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browserClientA"}})
    return results
 
options = ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument(r"--user-data-dir=C:\Users\Admin\AppData\Local\Google\Chrome\User Data\Default") #e.g. C:\Users\You\AppData\Local\Google\Chrome\User Data
service = Service("C:\Program Files\Google\Chrome\Application\chrome.exe")
# options.add_argument("--headless")
# options.add_argument("window-size=1000,1000")
driver = webdriver.Chrome(service=service, options=options) 
driver.get('https://google.com')
stealth(driver,
       user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.105 Safari/537.36',
       languages=["en-US", "en"],
       vendor="Google Inc.",
       platform="Win32",
       webgl_vendor="Intel Inc.",
       renderer="Intel Iris OpenGL Engine",
       fix_hairline=True,
       )
driver.get('https://ticketbox.vn/') 
print("loading")
# button = driver.find_element("xpath",'//*[@id="video-title-link"]/yt-formatted-string')
wait = WebDriverWait(driver, 0) 
button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sc-18zvx1f-0")))
button.click()
wait = WebDriverWait(driver, 1) 
driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browserClientA"}})
button  = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sc-1tm90jj-6")))
button.click()
wait = WebDriverWait(driver, 1)
input_field1 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'input[name="email"]')))
input_field1.send_keys("luchuongtam@gmail.com")
input_field2 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]')))
input_field2.send_keys("Tunglam123")
wait = WebDriverWait(driver, 1)
driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browserClientA"}})
button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="primary"]')))
button.click()
wait = WebDriverWait(driver, 5)
session = requests.Session()
completeBookingUrl, url_string = Booking(session)
urlTestCookie="https://ticketbox.vn/api/v2/user/current-user"
last_substring = url_string.rsplit('/', 1)[-1]
urlseat = "https://ticketbox.vn/api/v2/seatmap/"+last_substring
response = session.get(urlseat)
driver.get(completeBookingUrl)
time.sleep(random.uniform(0.5, 1))
if response.status_code == 200:
    try:
        data = response.json()
        # Serialize data to a string with width of 80 characters
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=4)
    except json.decoder.JSONDecodeError as e:
        print('Error decoding JSON response:', e)
        data = {}

with open('data.json') as f:
    data = json.load(f)
order_details = []
status = 1
order_expire_date = None
order_id = None
seats = find_seats_in_json(status, order_expire_date, order_id, data)
wait = WebDriverWait(driver, 5)
time.sleep(random.uniform(0.5, 2))
try:
    button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'table[ng-click="submitTicketInfo()"]')))
    button.click()
    time.sleep(random.uniform(0.5, 1))
except Exception as e:
    print('Error clicking on submit button: {}'.format(e))
wait = WebDriverWait(driver, 5)
time.sleep(500)
# Wait 3.5 on the webpage before trying anything 
 
# Wait for 3 seconds until finding the element 
# wait = WebDriverWait(driver, 0) 
# element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.woocommerce-loop-product__title'))) 
# print('Product name: ' + element.text) 
 

# Wait 4.5 seconds before scrolling down 700px 
 
# Wait 2 seconds before clicking a link 
# wait = WebDriverWait(driver, 0) 
# element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.woocommerce-loop-product__link'))).click() 

 
# # wait for 5 seconds until finding the element 
# wait = WebDriverWait(driver, 0) 
# element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'woocommerce-product-details__short-description'))) 
# print('Description: ' + element.text) 
# Wait 2 seconds before clicking a link
driver.close()