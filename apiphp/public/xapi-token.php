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
    //GETの場合、token一覧を返す
    if ($method == "GET"){

        $statement = $pdo->prepare("select tokenname, value from token;");
        $statement->execute();
        //配列化
        $valuearray = [];
        while($row = $statement->fetch(PDO::FETCH_ASSOC)){
            $valuearray[$row["tokenname"]] = $row["value"];
        }
        //JSON化
        $valuejson = json_encode($valuearray);
        echo $valuejson;
    }

    //POSTの場合、tokenを書き換える
    if ($method == "POST"){
        var_dump($_POST);
        #JSONを配列に
        $tokenarray = json_decode($_POST["token"]);
        var_dump($tokenarray);
        foreach ($tokenarray as $key => $value){
            $statement = $pdo->prepare("update token set value = :newtoken where tokenname = :tokenname;");
            $statement->bindValue(":tokenname", $key, PDO::PARAM_STR);
            $statement->bindValue(":newtoken", $value, PDO::PARAM_STR);
            $statement->execute();
        }
        
    }

}catch(Exception $e){
    echo $e;
}