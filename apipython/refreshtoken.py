import xtoken
import requests
import json
import datetime

#ログ用
print("================================")
print(datetime.datetime.now(), "JST")

#access_tokenはリフレッシュが必要
def refreshToken():
    URL = f"{xtoken.API_URL}xapi-token.php"
    apiresponse = requests.get(URL, headers=xtoken.MYHEADERS).json()

    URL = "https://api.twitter.com/2/oauth2/token"
    xresponse = requests.post(URL, headers={"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Basic {xtoken.ENCODE_CLIENT}"}, data={"refresh_token":apiresponse["REFRESH_TOKEN"], "grant_type":"refresh_token"}).json()

    URL = f"{xtoken.API_URL}xapi-token.php"
    tokenjson = json.dumps({"ACCESS_TOKEN":xresponse["access_token"], "REFRESH_TOKEN":xresponse["refresh_token"]})
    apiresponse = requests.post(URL, headers=xtoken.MYHEADERS, data={"token":tokenjson})

    return xresponse["access_token"]

refreshToken()
print("refresh token.")
