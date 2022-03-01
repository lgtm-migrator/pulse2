<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Settings saved for ", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$ini_array = parse_ini_file("/etc/mmc/plugins/urbackup.ini");
$username_urbackup = $ini_array['username'];
$password_urbackup = $ini_array['password'];

$interval_frequence_incremental_save = $_POST['update_freq_incr'];
$interval_frequence_full_save = $_POST['update_freq_full'];
$exclude_files = $_POST['exclude_files'];
$include_files = $_POST['include_files'];
$default_dirs = $_POST['default_dirs'];

$group_id = htmlspecialchars($_GET["groupid"]);

$settings_saver = array (
    "update_freq_incr" => $interval_frequence_incremental_save,
    "update_freq_full" => $interval_frequence_full_save,
    "exclude_files" => $exclude_files,
    "include_files" => $include_files,
    "default_dirs" => $default_dirs,
);

$group_id = "-".$group_id;

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


foreach ($settings_saver as $value => $item) {
    $name_data = $value;
    $value_data = $item;

    $url = "https://wva.siveo.net/urbackup/x?a=settings";
    $curlid = curl_init($url);

    curl_setopt($curlid, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($curlid, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($curlid, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($curlid, CURLOPT_POST, true);
    curl_setopt($curlid, CURLOPT_RETURNTRANSFER, true);

    $datas = [
        'sa'=>'clientsettings_save',
        't_clientid'=>$group_id,
        $name_data=>$value_data,
        'overwrite'=>"true",
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

    $saving = $result;
    $array = json_decode(json_encode($saving), true);

    $settings = $array['settings'];
}   

//-----------------------------------END SAVE SETTINGS
?>
<br>
<label><?php echo _T("Interval for incremental file backup", "urbackup"); ?></label>
<?php echo $settings['update_freq_incr']; ?>
<br>
<br>
<label><?php echo _T("Interval for full file backups", "urbackup"); ?></label>
<?php echo $settings['update_freq_full']; ?>
<br>
<br>
<label><?php echo _T("Excluded files", "urbackup"); ?></label>
<?php echo $settings['exclude_files']; ?>
<br>
<br>
<label><?php echo _T("Included files", "urbackup"); ?></label>
<?php echo $settings['include_files']; ?>
<br>
<br>
<label><?php echo _T("Default directories to backup", "urbackup"); ?></label>
<?php echo $settings['default_dirs']; ?>