import xtoken
import requests
import json
import time
import datetime

#フォローした相手が自分をフォローしているかを確認し、フォローされていなければフォローを解除する

#ログ用
print("================================")
print(datetime.datetime.now(), "JST")

#トークン
MYHEADERS = {"X-Auth": xtoken.API_TOKEN}

#確認対象ユーザー取得
URL = f"{xtoken.API_URL}xapi-checkfollow.php"
targetids = requests.get(URL, headers = MYHEADERS).json()

print(targetids)

ACCESS_TOKEN = xtoken.getToken()
XHEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
query = "ids=" + ",".join(targetids)
URL = f"https://api.twitter.com/2/users?" + query + "&user.fields=connection_status"
xresponse = requests.get(URL, headers=XHEADERS)
#rate制限を出力
print("フォロー確認", "rate上限:", xresponse.headers.get("x-rate-limit-limit"), " 残り回数:", xresponse.headers.get("x-rate-limit-remaining"), " 次回リセット時刻:", datetime.datetime.fromtimestamp(int(xresponse.headers.get("x-rate-limit-reset"))), " JST", " APIレスポンス取得時刻:", datetime.datetime.now(), "JST")
#まずdataの有無
if "data" in xresponse.json():
    xresponsedata = xresponse.json()["data"]
    #5件ない場合は、検索不能なIDがある
    if len(xresponsedata) < 5:
        print("===============================Not 5===============================")

    for target in xresponsedata:
        time.sleep(60 * 2)
        print(target)
        #connection_statusはない場合がある
        if "connection_status" in target and "followed_by" in target["connection_status"]:
            print("followed by ", target["id"])
            #フォローされていたらflagを1に
            URL = f"{xtoken.API_URL}xapi-checkfollow.php"
            followjson = json.dumps({"0" : target["id"]})
            apiresponse = requests.put(URL, headers=MYHEADERS, data={"follow":followjson})
        elif "connection_status" not in target or "followed_by" not in target["connection_status"]:
            print("unfollowed by ", target["id"])
            #されていなければフォロー解除
            #connection_statusがない場合も同様
            URL = f"https://api.twitter.com/2/users/{xtoken.MY_ID}/following/{target['id']}"
            xresponse = requests.delete(URL, headers=XHEADERS)
            #rate制限を出力
            print("フォロー解除", "rate上限:", xresponse.headers.get("x-rate-limit-limit"), " 残り回数:", xresponse.headers.get("x-rate-limit-remaining"), " 次回リセット時刻:", datetime.datetime.fromtimestamp(int(xresponse.headers.get("x-rate-limit-reset"))), " JST", " APIレスポンス取得時刻:", datetime.datetime.now(), "JST")
            #成功した場合
            if "data" in xresponse.json():
                URL = f"{xtoken.API_URL}xapi-checkfollow.php"
                deletejson = json.dumps({"0" : target["id"]})
                apiresponse = requests.put(URL, headers=MYHEADERS, data={"delete":deletejson})
            else:
                #失敗した場合
                print(xresponse.json(), "at delete follow")
        else:
            print("unknown", xresponsedata)

else:
    #dataがない場合、だいたいエラー
    print(xresponse.json(), "at check follow")

#API制限は100回/user 24h
