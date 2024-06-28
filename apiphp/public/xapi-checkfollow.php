<?php
require_once dirname(__FILE__, 2)."/pass/xapipass.php";

//token認証
checktoken($_SERVER["HTTP_X_AUTH"]);

try{
    //DB接続
    $pdo = new PDO("mysql:host=".getHost()."; dbname=".getDBName()."; charset=utf8mb4", getUser(), getPassword());
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);
    
    $method = $_SERVER["REQUEST_METHOD"];
    //GETの場合、3日経過したフォロワーを返す
    if ($method == "GET"){
        //フォロー解除候補ユーザー取得、フォロー解除API制限が5件/15分
        $now = time();
        $targetday = $now - (60 * 60 * 24 * 3); // 60秒 * 60分 * 24時間 * 3 = 3日
        //書式変換
        $targetday = date('Y-m-d', $targetday);
        $statement = $pdo->prepare("select userid from ChallengeAccount where date < :targetday and flag = 0 limit 5;");
        $statement->bindValue(":targetday", $targetday, PDO::PARAM_STR);
        $statement->execute();
        
        //配列化
        $useridarray = [];
        while($row = $statement->fetch(PDO::FETCH_ASSOC)){
            array_push($useridarray, $row["userid"]);
        }
        //JSON化
        $useridjson = json_encode($useridarray);
        echo $useridjson;
    }

    
    //PUTの場合、フォローされていたらflagを1に、されていなかったら2にする
    if ($method == "PUT"){
        parse_str(file_get_contents('php://input'), $useridjson);
        $followarray = json_decode($useridjson["follow"], true);
        $deletearray = json_decode($useridjson["delete"], true);
        //フォローしていたユーザー
        foreach ($followarray as $follow){
            $statement = $pdo->prepare("update ChallengeAccount set flag = 1 where userid = :followid;");
            $statement->bindValue(":followid", $follow, PDO::PARAM_STR);
            $statement->execute();
        }
        //フォローされていなかったユーザー
        foreach ($deletearray as $delete){
            $statement = $pdo->prepare("update ChallengeAccount set flag = 2 where userid = :deleteid;");
            $statement->bindValue(":deleteid", $delete, PDO::PARAM_STR);
            $statement->execute();
        }
    }
}catch(Exception $e){
    echo $e;
}