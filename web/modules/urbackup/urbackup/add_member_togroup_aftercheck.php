<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$group_id = $_POST['group'];
$client_id = htmlspecialchars($_GET["clientid"]);

$group_id_new = "-".$group_id;

$p = new PageGenerator(_T("Assign member to profil", 'urbackup'));
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
foreach($datas as $key=>$val)
{
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
    $result = (array)json_decode($response);

curl_close($curlid);

if(isset($result['session'], $result['success']) && $result['success'] == 1)
    $session = $result['session'];
//-----------------------------------END LOGIN

//-----------------------------------START ADD MEMBER TO GROUP FUNCTION
$url = "https://wva.siveo.net/urbackup/x?a=settings";
$curlid = curl_init($url);

curl_setopt($curlid, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curlid, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curlid, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curlid, CURLOPT_POST, true);
curl_setopt($curlid, CURLOPT_RETURNTRANSFER, true);

$datas = [
    'sa'=>"clientsettings_save",
    't_clientid'=>$group_id_new,
    'overwrite'=>"true",
    'group_mem_changes'=>$client_id.$group_id_new,
    'ses'=>$session,
];

$urlencoded = "";
foreach($datas as $key=>$val)
{
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
    $result = (array)json_decode($response);

curl_close($curlid);

$array = json_decode(json_encode($reviews), true);

$addgroup = $result;
$array_progress = json_decode(json_encode($addgroup), true);
//-----------------------------------END ADD MEMBER TO GROUP
?>
<br>
<?php

$url = 'main.php?module=urbackup&submod=urbackup&action=list_backups&clientid='.$client_id;

header("Location: ".$url);
?>