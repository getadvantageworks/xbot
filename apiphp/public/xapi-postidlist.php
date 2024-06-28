<?php
require_once dirname(__FILE__, 2)."/pass/xapipass.php";

//token認証
checktoken($_SERVER["HTTP_X_AUTH"]);

try{
    //DB接続
    $pdo = new PDO("mysql:host=".getHost()."; dbname=".getDBName()."; charset=utf8mb4", getUser(), getPassword());
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);
    $statement = $pdo->prepare("select postid, count from ChallengePost;");
    $statement->execute();
    //配列化
    $postidarray = [];
    $countarray = [];
    while($row = $statement->fetch(PDO::FETCH_ASSOC)){
        array_push($postidarray, $row["postid"]);
        array_push($countarray, $row["count"]);
    }
    $method = $_SERVER["REQUEST_METHOD"];
    //GETの場合、挑戦済ポスト一覧と回数を返す
    if ($method == "GET"){
        $postcountarray = [];
        for ($i = 0; $i < count($postidarray); $i++){
            $postcountarray[$postidarray[$i]] = $countarray[$i];
        }
        //JSON化
        $postidjson = json_encode($postcountarray);
        echo $postidjson;
    }

    //POSTの場合、挑戦済ポストを追加する
    if ($method == "POST"){
        #JSONを配列に
        $postarray = json_decode($_POST["challengeposts"]);
        foreach ($postarray as $post){
            //重複していなければcount=1、していればcount++
            if(array_search($post, $postidarray) === false){
                $statement = $pdo->prepare("insert into ChallengePost(postid, date, count) values(:postid, CURRENT_DATE, 1);");
                $statement->bindValue(":postid", $post, PDO::PARAM_STR);
                $statement->execute();
            }else{
                $statement = $pdo->prepare("update ChallengePost set count = :newcount where postid = :updateid;");
                $statement->bindValue(":newcount", $countarray[array_search($post, $postidarray)] + 1, PDO::PARAM_INT);
                $statement->bindValue(":updateid", $post, PDO::PARAM_STR);
                $statement->execute();
            }
        }
    }
}catch(Exception $e){
    echo $e;
}
?>