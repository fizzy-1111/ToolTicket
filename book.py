import requests
from bs4 import BeautifulSoup
import json
import hmac
import hashlib
import base64
import time
from selenium import webdriver 
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
import http.cookiejar
from pypasser import reCaptchaV3
def login(email, password):
    # Define the endpoint URLs
    login_url = "https://api-movie.ticketbox.vn/v1/users/login/email"
    device_url = "https://api-movie.ticketbox.vn/v1/users/devices"
    # Define the payload for the login request
    login_payload = {
        "email": email,
        "password": password,
    }

    # Define the payload for the device registration request
    device_payload ={
        "device_id":"8ce91fe4409360a86d3daf1fe9a39cec",
        "push_token":"",
        "api_key":"1JJ1QO5JLWQ2FNVWE73IKG0PF5YAONSP",
        "requested_at":"1687882213194",
        "signature":"2f13ebb99e562399054f24b94fb694c440ac3bdddf22d3ffc46777f608d03c5d"
    }
    # Send the device registration request first
    device_res = requests.post(device_url, json=device_payload)

    # Extract the API key from the device registration response
    deviceToken = device_res.json()["data"]["device_token"]

    headers = {
        "X-Tb-Device-Token": deviceToken
    }

    # Add the API key to the login payload
    session = requests.Session()
    # Send the login request with the updated payload
    login_res = session.post(login_url, json=login_payload,headers=headers)
    return session,login_res
def Booking(session):
# Extract the access token from the login response
    HotShow_url = "https://api.ticketbox.vn/v1.0/events/top-banner"
    hotshow_res = session.get(HotShow_url)
    hotshow_data = hotshow_res.json()["data"]
    for show in hotshow_data:
        if "MARK" in show["name"]:
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

def find_seat_in_json(seat_id, data):
    for section in data['sections']:
        for row in section['rows']:
            for seat in row['seats']:
                if seat['id'] == seat_id:
                    return {
                        'section_id': section['id'],
                        'row_id': row['id']
                    }
    return None
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
                    if(len(results)>=4):
                        return results
                    result = {
                        'section_id': section['id'],
                        'row_id': row['id'],
                        'seat_id': seat['id'],
                        'seat_name': seat['name'],
                        'section_name': section['name'],
                        'row_name': row['name'],
                        'ticketTypeId':section['ticketTypeId'],
                        'status': 1,
                    }
                    seat['status'] = 3
                    results.append(result)
    return results
def create_order_details(data):
    order_details = []
    status = 1
    order_expire_date = None
    order_id = None
    seats = find_seats_in_json(status, order_expire_date, order_id, data)
    for seat in seats:
        if seat:
            ticket_type_id = seat['ticketTypeId']
            section_id = seat['section_id']
            section_name = seat['section_name']
            row_name = seat['row_name']
            quantity = 1

            # Check if order_detail already exists for the current ticketTypeId
            order_detail = next((item for item in order_details if item["ticketTypeId"] == ticket_type_id), None)
            if order_detail is None:
                # Create a new order_detail if it does not exist
                order_detail = {
                    'ticketTypeId': ticket_type_id,
                    'quantity': 0,
                    'sections': []
                }
                order_details.append(order_detail)

            # Update the quantity and sections for the order_detail
            order_detail['quantity'] += quantity
            section = next((item for item in order_detail['sections'] if item["sectionId"] == section_id), None)
            if section is None:
                section = {
                    'sectionId': section_id,
                    'quantity': 0,
                    'isReserveSeating': True,
                    'seats': []
                }
                order_detail['sections'].append(section)

            section['quantity'] += quantity
            print(seat['seat_id'])
            section['seats'].append({
                'id': seat['seat_id'],
                'name': seat['seat_name'],
                'rowName': row_name,
                'sectionName': section_name,
                'status': None,
            })

    return {'orderDetails': order_details}
#In the given Url , get all the url that has the word api in it
# session,loginData = login("luchuongtam@gmail.com", "Tunglam123")
cookie_jar = http.cookiejar.CookieJar()
session = requests.Session()
session.cookies = cookie_jar

headers = json.load(open("cookie.json","r"))
data_str = json.dumps(headers, indent=4)
# Write data string to a file named 'data.txt'
with open('cookie.txt', 'w') as f:
    f.write(data_str)
# payload ={"buyerInfo":{"email":"luchuongtam@gmail.com","firstName":"Nguyen","lastName":"Lam","phoneNumber":"0981457953"},"subcribeMail":True,"paymentInfo":{"paymentType":16,"deliveryInfo":{"note":None,"fullAddress":None,"address":None,"cityId":0,"districtId":0,"fee":0,"wardId":0},"officePickupInfo":{"note":None,"deadline":"2023-06-30T18:30:00+07:00"},"internetBankingInfo":{"bankCode":None},"payooInfo":{"billingCode":None,"expireDate":"2023-07-01T22:37:09.3648564+07:00"},"one23Info":{"counter":None,"encryptedData":None,"expireDate":"2023-06-29T22:37:09.3648564+07:00"},"omiseInfo":{"omiseToken":None},"bankTransferInfo":{"billingCode":None,"expireDate":"2023-06-29T22:37:09.3648564+07:00"},"cybersourceInfo":{"billingInfo":None,"card":None,"statusPayment":None,"returnMessage":None,"returnCode":None},"smartlinkInfo":{"isSuccess":None,"isCancelled":None,"message":None},"twoC2PInfo":{"isSuccess":None,"statusDescription":None,"card":{}},"unipayAlipayInfo":{"paymentChannel":""},"moMoInfo":{"statusDescription":""}},"officeId":1,"receivingMethod":{"receivingMethod":1,"noteDeliver":None},"secretKey":""}
completeBookingUrl, url_string = Booking(session)
urlTestCookie="https://ticketbox.vn/api/v2/user/current-user"
last_substring = url_string.rsplit('/', 1)[-1]
urlseat = "https://ticketbox.vn/api/v2/seatmap/"+last_substring
response = session.get(urlseat, headers=headers)
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

order_details = create_order_details(data)
with open('orders.json', 'w') as f:
    json.dump(order_details, f, indent=4)

with open('orders.json') as f:
    payload = json.load(f)

# Set the securityToken field with the encoded signature
payload["securityToken"] ="wyLwOLqIQua5_TcHzDHW2efzkAfRwyCPc6tl5nC2fKKMESOV0fXNmIMWcSr7azzcayc85N4ZWhQ3poqbuCY3Z_uoAKn5OOB7Ewc_1I5QblM1:EEJ-RgdN90JvU0mLvLiEQNmViBFqmZgUUxOpcgDnjYcmKnn_556KiKIdgJILK2P8Ra3rO4lLncAltQC8jAY25OL8S31-j_HYJAH45agkumLu7Kp-Ex4aVIQ7uYOZhqVy0"
payload["MobileOS"]=None
payload["isWidget"]=False
payload["capcha"]="03AAYGu2SbplB7Nh0geUsqXmp4-CsmYVeM2Kpx5q58P_e0IVIhAZHGC0xZxKo-mT5hihqKv58Fj-yXhB5ltUgJd9czTx0zDhqqqn2-veqdzR3xma-St-QpapQEhM1WivBX-ikYf_T6QENLmEse58zQOTnwjJj8iC-CtdKUxiAu9yPHoP7N5XTS3y-dcMwIr9_dPfd7AoTkHgx6DvSdj2bFx9DACsD3tjowAUdQzQrxcQeYc9nEvjUNAue3TOPKUNz2S4Bw_m-0T3oR8oT0bKsklv2NqBO4yZK3KufYW8wucPrkOcyqBY4q6uDkSwsQ101wmBDGlaVgPvGixL1f3ofpS3iaIekWfVLSSI_HwenWc26vf9sUIX9ZiRf8ctjlj0yY0n3Nrbs4aRT5NG0RBteuyTNUSqe5vnnArySyBqRPscI7lDpx0Xfg_QZtTxXGPFQtPTn512Yr1kDR8D5dJ-rxE95yB-m-1o9rMzlGFlFyWISzD6t2HeN1dgCKACib2D-LM_l18tizQObllSH_rZFtk5Q3Hf3q8QLlzvF5HCIlSaS3BzKUOgYaySdCe2u5TtgA9XrZhnGD8ZJUWrV-z-vfHMg6hMahEu2p-bPgFULQCN4VN-9YruGalbuLDJMl3N_6WQ0liZKAMyQrzb8ovWs49MeLrptVvwXMpRrTlgg6DohUKKqr0Hp4oAyFtl2SnqYv86WQOJuhQUKEWSO1tlT8HdxYryXDl5engHqP3XeneseXGxVXJ0jN0WQLO4UmbpC0-_pSYEg-meGQ9hopjPyA8qkizZPLMSmWGJFVmfLcdo2v8tiZR3mXNifkOnFgrES-hri9IAq9DP7H10qYfZh7iss0SUDFN0EcIHvjGKwA_692Rby_A8y0m18zn7xas_QFe7vmp6UpZ08DlLfSqGfxCnyJXPs6H2MeGX10nC0Hiwl6kyYQASyUacSEvXgOYUdNzeM1xILjOtZZ4JOl80O59uLKwPCibpRmz-50_ZH-81wRZd_P7w_Fws_ZUtX81FtKz-4BGDj8p2_fChRJtvxmPNL-VF_8WDX1Yvc3pAOct_BURfteMROopaV8ZcFGEEbH0mrU0iLF_fuGdL1woP19_O-j6hwecV9TUqD9-WygZaKkHU1gxes9FdDTJcfubt9BCLcPQ5yyLATL4PC2N5g-U-zoMaUoHaLl2zKbxToLogUmwvzRlDr3eoCdHTFez5OXK4TKGP9IN1FmrKQ-5F6VDG2YC_CEYHQx8UKRH_6IIG70s1Iw0P9f8UQxjkLXXL_md4CbunDGnM5P3U3bxrFZZGsgZlWWdqjQ7PJKsMHCRG_ITKk1rD9G3Esx6NEU-B5RGjKL8nndheZI"

urlSubmitTicket="https://ticketbox.vn/api/"+url_string+"/submit-ticket-info"
response = session.post(urlSubmitTicket, json=payload,headers=headers)
print(response.content)
orderPayload={"buyerInfo":{"email":"luchuongtam@gmail.com","firstName":"Nguyen","lastName":"Lam","phoneNumber":"0981457953"},"subcribeMail":True,"paymentInfo":{"paymentType":16,"deliveryInfo":{"note":None,"fee":0,"fullAddress":None,"address":None,"cityId":0,"districtId":0,"wardId":0},"officePickupInfo":{"note":None,"deadline":None},"internetBankingInfo":None,"payooInfo":{"billingCode":None,"expireDate":"0001-01-01T00:00:00+07:00"},"one23Info":{"counter":{"counterCode":None},"expireDate":"0001-01-01T00:00:00+07:00","encryptedData":None,"refNo1":None,"refNo2":None},"omiseInfo":{"omiseToken":None,"chargeToken":None},"bankTransferInfo":{"billingCode":None,"expireDate":"0001-01-01T00:00:00+07:00"},"cybersourceInfo":{"statusPayment":None,"returnMessage":None,"returnCode":None,"card":{"brand":None,"cardType":"","expirationMonth":None,"expirationYear":None,"securityCode":None,"number":None,"maskedValidatedNumber":""},"billingInfo":{"phone":None,"email":None,"address":None,"city":None,"country":None,"state":None,"zipCode":None}},"smartlinkInfo":{"statusPayment":None,"isSuccess":False,"isCancelled":True},"twoC2PInfo":{"statusPayment":None,"statusDescription":None,"isSuccess":False},"unipayAlipayInfo":{"statusPayment":None,"statusDescription":None,"paymentChannel":None,"isSuccess":False},"moMoInfo":{"statusDescription":""}},"officeId":1,"receivingMethod":{"receivingMethod":1,"noteDeliver":None},"secretKey":""}

urlOrder = "https://ticketbox.vn/api/" + url_string + "/submit-order"
currentOrder="https://ticketbox.vn/api/" + url_string + "/current-order"

headers["Accept-Language"]="en-US,en;q=0.9,vi;q=0.8"
headers["Referer"]=completeBookingUrl
headers["Scheme"]="https"
headers["Authority"]="ticketbox.vn"
headers["Accept"]="application/json, text/plain, */*"
headers["Sec-Ch-Ua"]="\" Not A;Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\""
headers["Sec-Ch-Ua-Mobile"]="?0"
headers["Sec-Ch-Ua-Platform"]="\"Windows\""
headers["Content-Type"]="application/json;charset=UTF-8"
headers["Origin"]="https://ticketbox.vn"
headers["Sec-Fetch-Site"]="same-origin"
headers["Sec-Fetch-Mode"]="cors"
headers["X-Requested-With"]="XMLHttpRequest"
headers["Sec-Fetch-Dest"]="empty"
headers["User-Agent"]="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
response = session.post(urlOrder, json=orderPayload, headers=headers)
try:
    response = session.post(urlOrder, json=orderPayload, headers=headers)
    print(response.content)
except requests.exceptions.ConnectionError:
    response.status_code = "Connection refused"
# response=session.get(currentOrder,headers=headers)
# print(response.content)
# print(response.content)


