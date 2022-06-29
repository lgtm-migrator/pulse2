<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$group_id = htmlspecialchars($_GET["groupid"]);
$group_name = htmlspecialchars($_GET["groupname"]);

$p = new PageGenerator(_T("Settings for ".$group_name, 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$group_id_new = "-".$group_id;

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
    'sa'=>'clientsettings_save',
    't_clientid'=>$group_id_new,
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

$res = $result;
$array = json_decode(json_encode($res), true);

$settings = $array['settings'];

//-----------------------------------END SAVE SETTINGS

$interval_incremental_backup = $settings['update_freq_incr']/3600;
$interval_full_backup = $settings['update_freq_full']/86400;

$current_value_exclude_files = "";
$current_value_include_files = "";
$current_value_default_dirs = "";

if ($settings['exclude_files'] != "")
{
    $current_value_exclude_files = "Current value: ";
}

if ($settings['include_files'] != "")
{
    $current_value_include_files = "Current value: ";
}

if ($settings['default_dirs'] != "")
{
    $current_value_default_dirs = "Current value: ";
}

?>
<br>
<form name="form" action="main.php?module=urbackup&amp;submod=urbackup&amp;action=validate_edit_group&amp;groupid=<?php echo $group_id; ?>&amp;groupname=<?php echo $group_name; ?>&amp;current_inter_incr_backup=<?php echo $interval_incremental_backup; ?>&amp;current_inter_full_backup=<?php echo $interval_full_backup; ?>&amp;current_exclude_files=<?php echo $settings['exclude_files']; ?>&amp;current_include_files=<?php echo $settings['include_files']; ?>&amp;current_default_dirs=<?php echo $settings['default_dirs']; ?>" method="post">
    <label><?php echo _T("Interval for incremental file backups (hour)", "urbackup"); ?></label><input placeholder="Current value: <?php echo $interval_incremental_backup; ?>" type="text" name="update_freq_incr" id="update_freq_incr"/><br>
    <label><?php echo _T("Interval for full file backups (day)", "urbackup"); ?></label><input placeholder="Current value: <?php echo $interval_full_backup; ?>" type="text" name="update_freq_full" id="update_freq_full"/><br>
    <label><?php echo _T("Excluded files", "urbackup"); ?></label><input placeholder="<?php echo $current_value_exclude_files; ?><?php echo $settings['exclude_files']; ?>" type="text" name="exclude_files" id="exclude_files"/><br>
    <label><?php echo _T("Included files", "urbackup"); ?></label><input placeholder="<?php echo $current_value_include_files; ?><?php echo $settings['include_files']; ?>" type="text" name="include_files" id="include_files"/><br>
    <label><?php echo _T("Default directories to backup", "urbackup"); ?></label><input placeholder="<?php echo $current_value_default_dirs; ?><?php echo $settings['default_dirs']; ?>" type="text" name="default_dirs" id="default_dirs"/><br><br>
    <input type="submit" value="Save">
</form>
