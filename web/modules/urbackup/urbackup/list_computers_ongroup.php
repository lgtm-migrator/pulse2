
<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$group_id = htmlspecialchars($_GET["groupid"]);
$group_name = htmlspecialchars($_GET["groupname"]);

$p = new PageGenerator(_T("List user on profil ".$group_name, 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$ini_array = parse_ini_file("/etc/mmc/plugins/urbackup.ini");
$username_urbackup = $ini_array['username'];
$password_urbackup = $ini_array['password'];

//-----------------------------------START LOGIN FUNCTION
$url = "https://wva.siveo.net/urbackup/x?a=login";

$curlid = curl_init($url);

curl_setopt($curlid, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curlid, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curlid, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curlid, CURLOPT_POST, true);
curl_setopt($curlid, CURLOPT_RETURNTRANSFER, true);
$datas = [
'username'=>$username_urbackup,
'password'=>$password_urbackup,
'plainpw'=>1
];

$urlencoded = "";
foreach($datas as $key=>$val){
$urlencoded .= $key.'='.$val.'&';
}
rtrim($urlencoded, '&');

curl_setopt($curlid, CURLOPT_POSTFIELDS, $urlencoded);
$response = curl_exec($curlid);

if (curl_errno($curlid)) 
{
    echo 'Requête échouée : '.curl_error($curlid).'<br>';
    $result = [];
}
else
{
$result = (array)json_decode($response);
}

curl_close($curlid);

if(isset($result['session'], $result['success']) && $result['success'] == 1){
    $session = $result['session'];
}
//-----------------------------------END LOGIN

//-----------------------------------START SAVE SETTINGS FUNCTION
$url = "https://wva.siveo.net/urbackup/x?a=settings";
$curlid = curl_init($url);

curl_setopt($curlid, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curlid, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curlid, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curlid, CURLOPT_POST, true);
curl_setopt($curlid, CURLOPT_RETURNTRANSFER, true);

$datas = [
    'sa'=>'general',
    'ses'=>$session,
];

$urlencoded = "";
foreach($datas as $key=>$val){
$urlencoded .= $key.'='.$val.'&';
}
rtrim($urlencoded, '&');

curl_setopt($curlid, CURLOPT_POSTFIELDS, $urlencoded);
$response = curl_exec($curlid);

$result = (array)json_decode($response);

curl_close($curlid);

$settings = $result;
$array = json_decode(json_encode($settings), true);

$clients = $array['navitems']['clients'];
//-----------------------------------END SAVE SETTINGS
?>
<br>
<?php
foreach($clients as $client)
{
    if ($client['group'] == $group_id)
    {
        print_r($client['name']);
        echo '<br>';
    }
}
?>