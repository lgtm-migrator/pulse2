<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$clientname = htmlspecialchars($_GET["cn"]);
$jidMachine = htmlspecialchars($_GET["jid"]);

$p = new PageGenerator(_T("Check if ".$clientname." exist", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$clients = xmlrpc_get_backups_all_client();
$clients = $clients["clients"];

foreach ($clients as $client)
{
    if ($client["name"] == $clientname)
    {
        $exist = "true";
        $id = $client["id"];
    }
    else
        $exist = "false";
}

$ini_array = parse_ini_file("/etc/mmc/plugins/urbackup.ini");
$username_urbackup = $ini_array['username'];
$password_urbackup = $ini_array['password'];
$url_urbackup = $ini_array['url'];

//-----------------------------------START LOGIN FUNCTION
$url = $url_urbackup."?a=login";

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
$url = $url_urbackup."?a=settings";
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

$groups = $array['navitems']['groups'];

?>
<br>
<?php

$url = 'main.php?module=urbackup&submod=urbackup&action=list_backups&clientid='.$id;

if ($exist == "true")
{
    header("Location: ".$url);
    echo "<a href='main.php?module=urbackup&amp;submod=urbackup&amp;action=list_backups&amp;clientid=".$id."'>Go to user backups</a>";
}
else
{
    $create_client = xmlrpc_add_client($clientname);

    if ($create_client["already_exists"] == "1") 
    {
        print_r(_T("User already exists" ,"urbackup"));
        header("Location: ".$url);
    }
    else
    {
        $check_client = xmlrpc_check_client($jidMachine, $create_client["new_clientid"], $create_client["new_authkey"]);
        ?>
        <div style="display:flex">
            <form name="form" action="main.php?module=urbackup&amp;submod=urbackup&amp;action=add_member_togroup_aftercheck&amp;clientid=<?php echo $create_client["new_clientid"]; ?>" method="post">
                <div>
                    <h3><?php echo _T("Computer name", "urbackup"); ?></h3>
                    <ul id="outProfil" name="outProfil" class="ui-sortable" style="background-color: white; width: 250px; height: 200px; padding-top: 10px; margin-right: 30px;">
                        <?php echo $create_client["new_clientname"]; ?>
                    </ul>
                </div>
                <div>
                    <h3><?php echo _T("Choose profil to computer", "urbackup"); ?></h3>
                    <select name="group" id="group">
                        <?php
                        foreach($groups as $group)
                        {
                            echo '<option value="'.$group['id'].'">'.$group['name'].'</option>';
                        }
                        ?>
                    </select>
                    <input type="submit" value="Add <?php echo $create_client["new_clientname"]; ?> on profil">
                </div>
            </form>
        </div>
        <?php
    }
}
?>