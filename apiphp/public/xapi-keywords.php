<?php
require_once dirname(__FILE__, 2)."/pass/xapipass.php";

//token認証
checktoken($_SERVER["HTTP_X_AUTH"]);

try{
    //DB接続
    $pdo = new PDO("mysql:host=".getHost()."; dbname=".getDBName()."; charset=utf8mb4", getUser(), getPassword());
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);

    //キーワード取得
    $statement = $pdo->prepare("select word from SearchKeywords;");
    $statement->execute();
    //配列化
    $keywordsarray = [];
    while($row = $statement->fetch(PDO::FETCH_ASSOC)){
        array_push($keywordsarray, $row["word"]);
    }

    //NGワード取得
    $statement = $pdo->prepare("select word from NGKeywords;");
    $statement->execute();
    //配列化
    $ngarray = [];
    while($row = $statement->fetch(PDO::FETCH_ASSOC)){
        array_push($ngarray, $row["word"]);
    }
    //JSON化
    $wordarray = [];
    $wordarray["key"] = $keywordsarray;
    $wordarray["ng"] = $ngarray;
    $wordsjson = json_encode($wordarray);
    echo $wordsjson;
}catch(Exception $e){
    echo $e;
}
