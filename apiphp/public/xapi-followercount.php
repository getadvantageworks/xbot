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
    
    //フォロワーを記録
    if ($method == "POST"){
        $statement = $pdo->prepare("insert into FollowerCount(count, date) values(:count, CURRENT_TIMESTAMP);");
        $statement->bindValue(":count", $_POST["count"], PDO::PARAM_INT);
        $statement->execute();
    }
    
}catch(Exception $e){
    echo $e;
}