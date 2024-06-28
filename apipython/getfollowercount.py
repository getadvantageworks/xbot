import xtoken
import requests
import datetime

#ログ用
print("================================")
print(datetime.datetime.now(), "JST")

#トークン
XHEADERS = {"Authorization": f"Bearer {xtoken.BEARER_TOKEN}"}
MYHEADERS = {"X-Auth": xtoken.API_TOKEN}

#フォロワー数を取得
URL = f"https://api.twitter.com/2/users/{xtoken.MY_ID}?user.fields=public_metrics"
xresponse = requests.get(URL, headers=XHEADERS).json()
if "data" in xresponse:
    followercount = xresponse["data"]["public_metrics"]["followers_count"]
    print(followercount)

    #DBに送信
    URL = f"{xtoken.API_URL}xapi-followercount.php"
    apiresponse = requests.post(URL, headers=MYHEADERS, data={"count":followercount})

else:
    print(xresponse, "at get follower count")