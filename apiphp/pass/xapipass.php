<?php
//DB情報

function getHost():string
{
    return "host";
}

function getDBName():string
{
    return "DBName";
}

function getUser():string
{
    return "user";
}

function getPassword():string
{
    return "password";
}

//アクセス認証
function checktoken($token){
    try{
        //DB接続
        $pdo = new PDO("mysql:host=".getHost()."; dbname=".getDBName()."; charset=utf8mb4", getUser(), getPassword());
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $pdo->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);
    
        //トークンハッシュ取得
        $statement = $pdo->prepare("select tokenhash from User where id = 1;");
        $statement->execute();
        $row = $statement->fetch(PDO::FETCH_ASSOC);
        $tokenhash = $row["tokenhash"];
        
        //照合
        if(!password_verify($token, $tokenhash)){
            echo "error";
            exit();
        }
    
    }catch(Exception $e){
        echo $e;
    }
}