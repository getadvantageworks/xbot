import xtoken
import requests
import datetime
import time
import json
import random

#指定のキーワードを含むポストに反応している(RP、いいね)ユーザーを探し、フォローする

#ログ用
print("================================")
print(datetime.datetime.now(), "JST")

#トークン
XHEADERS = {"Authorization": f"Bearer {xtoken.BEARER_TOKEN}"}
MYHEADERS = {"X-Auth": xtoken.API_TOKEN}

#検索文字列とNG文字列を取得
URL = f"{xtoken.API_URL}xapi-keywords.php"
searchKeywords = requests.get(URL, headers = MYHEADERS).json()
key = searchKeywords["key"]
ng = searchKeywords["ng"]

#検索クエリはUTC
now = datetime.datetime.now(datetime.timezone.utc)
#RPされる猶予時間を設定
endtime = now - datetime.timedelta(hours = 1)
#過去のポストを掘り返さない
starttime = now - datetime.timedelta(days = 6)

#ポスト検索、ポストID集合作成
#重複がないようにset
targetpostidset = set()
for word in key:
    #話題のポストを取りたい
    #最大取得数、API制限に注意
    MAX_RESULTS = 50
    URL = f"https://api.twitter.com/2/tweets/search/recent?query={word}%20-{','.join(ng)}&start_time={starttime.isoformat().split('.')[0]}Z&end_time={endtime.isoformat().split('.')[0]}Z&max_results={MAX_RESULTS}&sort_order=relevancy&tweet.fields=public_metrics"
    xresponse = requests.get(URL, headers=XHEADERS).json()
    #中身があったとき
    if "data" in xresponse:
        print(word, " 検索ヒット数", len(xresponse["data"]))
        for post in xresponse["data"]:
            #リポストされていなければ無視
            if post["public_metrics"]["retweet_count"] > 0:
                targetpostidset.add(post["id"])
    else:
        #中身がなかったとき、エラーだったとき、出力しておく
        print(xresponse, "at get post about ", word)
    time.sleep(1)

print("候補ポスト数", len(targetpostidset))
#setをlist化
targetpostidlist = list(targetpostidset)

#チェックしたポストを取得
URL = f"{xtoken.API_URL}xapi-postidlist.php"
apiresponse = requests.get(URL, headers = MYHEADERS).json()

#チェック回数を紐づけ
prioritydict = dict()
for post in targetpostidlist:
    #チェックしたことがあればその回数を紐づける
    if post in apiresponse:
        prioritydict[post] = int(apiresponse[post])
    else:
        #チェックしたことがなければ0にする
        prioritydict[post] = 0


#チェックした回数が少ない順にソート
sortedtuple = sorted(prioritydict.items(), key = lambda x:x[1])
#タプルからリストに
targetpostidlist = list()
for i in range(len(sortedtuple)):
    targetpostidlist.append(sortedtuple[i][0])

#チェックしたポストをDBに記録
URL = f"{xtoken.API_URL}xapi-postidlist.php"
postjson = json.dumps({i:targetpostidlist[i] for i in range(0,len(targetpostidlist))})
apiresponse = requests.post(URL, headers=MYHEADERS, data={"challengeposts":postjson})
print(apiresponse.text)

#見つかったポストをリポスト・いいねしているユーザーID集合を作成
#重複がないようにset

#リポストから
targetuseridset = set()
for i in range(min(5, len(targetpostidlist))):
    #このAPIはBasicで5件/15分
    URL = f"https://api.twitter.com/2/tweets/{targetpostidlist[i]}/retweeted_by"
    xresponse = requests.get(URL, headers=XHEADERS).json()
    
    #中身がない場合もあるので確認
    if "data" in xresponse:
        for user in xresponse["data"]:
            targetuseridset.add(user["id"])
    #リクエスト上限となったときなどのエラーの処理、出力しておく
    else:
        print(xresponse, "at getting RP")
    
    #Too many requests回避策
    time.sleep(1)

print("RPユーザー数", len(targetuseridset))


#setをlist化
targetuseridlist = list(targetuseridset)
#候補のうち、すでにフォローを試みている対象を除外する
#フォロー挑戦済取得
URL = f"{xtoken.API_URL}xapi-idlist.php"
alreadyusers = requests.get(URL, headers=MYHEADERS).json()
for user in targetuseridlist:
    #重複していれば除去
    if user in alreadyusers:
        targetuseridlist.remove(user)

#RPだけで5人いなかった場合、いいねを検証
if len(targetuseridlist) < 5:
    #いいね
    for i in range(min(25, len(targetpostidlist))):
        #このAPIはBasicで25件/15分
        URL = f"https://api.twitter.com/2/tweets/{targetpostidlist[i]}/liking_users"
        xresponse = requests.get(URL, headers=XHEADERS).json()
        #中身がない場合もあるので確認
        if "data" in xresponse:
            for user in xresponse["data"]:
                targetuseridset.add(user["id"])
        #リクエスト上限となったときなどのエラーの処理、出力しておく
        else:
            print(xresponse, "at getting like")
        
        #Too many requests回避策
        time.sleep(1)

    #重複除去
    for user in targetuseridlist:
        #重複していれば除去
        if user in alreadyusers:
            targetuseridlist.remove(user)


print("除去前ユーザー数", len(targetuseridset))

#setをlist化
targetuseridlist = list(targetuseridset)


#候補のうち、すでにフォローを試みている対象を除外する
#フォロー挑戦済取得
URL = f"{xtoken.API_URL}xapi-idlist.php"
alreadyusers = requests.get(URL, headers=MYHEADERS).json()
for user in targetuseridlist:
    #重複していれば除去
    if user in alreadyusers:
        targetuseridlist.remove(user)

print("候補ユーザー数", len(targetuseridlist))

#ユーザーID集合から実際にフォローするユーザーを抽出する
#とりあえずランダム
#5回/15分
MAX_FOLLOW_VOLUME = 5
followtargetlist = random.sample(targetuseridlist, min(MAX_FOLLOW_VOLUME, len(targetuseridlist)))
#フォローする
#API制限が15分で5件
apidict = dict()
index = 0

for target in followtargetlist:
    #Too Many Requestsが発生しやすい
    time.sleep(60 * 3)
    ACCESS_TOKEN = xtoken.getToken()
    URL = f"https://api.twitter.com/2/users/{xtoken.MY_ID}/following"
    targetjson = json.dumps({"target_user_id" : target})
    xresponse = requests.post(URL, headers={"Authorization": f"Bearer {ACCESS_TOKEN}", "content-type": "application/json"}, data = targetjson)
    #rate制限を出力
    print("rate上限:", xresponse.headers.get("x-rate-limit-limit"), " 残り回数:", xresponse.headers.get("x-rate-limit-remaining"), " 次回リセット時刻:", datetime.datetime.fromtimestamp(int(xresponse.headers.get("x-rate-limit-reset"))), " JST", " APIレスポンス取得時刻:", datetime.datetime.now(), "JST")
    #成功判定
    if "data" in xresponse.json():
    #成功したら格納
        apidict[index] = target
        index = index + 1
    else:
        #リクエスト上限となったときなどのエラーの処理、出力しておく
        print(xresponse.json(), "at following")

#空でなければ実行
print("フォロー対象", apidict)
if len(apidict) > 0:
    apijson = json.dumps(apidict)
    URL = f"{xtoken.API_URL}xapi-idlist.php"
    apiresponse = requests.post(URL, headers=MYHEADERS, data = {"follow" : apijson})

