import requests
import json

MY_ID = "XXX"
BEARER_TOKEN = "XXXX"
API_KEY = "XXXX"
API_KEY_SECRET = "XXX"
CLIENT_ID = "XXX"
CLIENT_SECRET = "XXX"
ACCESS_TOKEN_SECRET = "XXXW"
API_URL = "XXX"
API_TOKEN = "XXX"

MYHEADERS = {"X-Auth": API_TOKEN}

ENCODE_CLIENT = "XXX"

#現在のアクセストークンを取得
def getToken():
    URL = f"{API_URL}xapi-token.php"
    apiresponse = requests.get(URL, headers=MYHEADERS).json()

    return apiresponse["ACCESS_TOKEN"]