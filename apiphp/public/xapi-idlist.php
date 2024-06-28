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
    //GETの場合、フォロー挑戦済ユーザー一覧を返す
    if ($method == "GET"){
        //フォロー挑戦済ユーザー取得
        $statement = $pdo->prepare("select userid from ChallengeAccount;");
        
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

    //POSTの場合、フォロー挑戦済ユーザーを追加する
    if ($method == "POST"){
        //フォロー挑戦済ユーザー取得
        $statement = $pdo->prepare("select userid from ChallengeAccount;");
        $statement->execute();
        //配列化
        $useridarray = [];
        while($row = $statement->fetch(PDO::FETCH_ASSOC)){
            array_push($useridarray, $row["userid"]);
        }
        #JSONを配列に
        $followarray = json_decode($_POST["follow"]);
        foreach ($followarray as $follow){
            //重複確認
            if(in_array($follow, $useridarray) === false){
                $statement = $pdo->prepare("insert into ChallengeAccount(userid, date, flag) values(:follow, CURRENT_DATE, 0);");
                $statement->bindValue(":follow", $follow, PDO::PARAM_STR);
                $statement->execute();
            }
        }
    }
    
}catch(Exception $e){
    echo $e;
}