<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("List Backups by Client", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$ini_array = parse_ini_file("/etc/mmc/plugins/urbackup.ini");
$username_urbackup = $ini_array['username'];
$password_urbackup = $ini_array['password'];

$client_id = htmlspecialchars($_GET["clientid"]);

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

//-----------------------------------START GET_BACKUPS FUNCTION
$url = "https://wva.siveo.net/urbackup/x?a=backups";
$curlid = curl_init($url);

curl_setopt($curlid, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curlid, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curlid, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curlid, CURLOPT_POST, true);
curl_setopt($curlid, CURLOPT_RETURNTRANSFER, true);

$datas = [
    'sa'=>'backups',
    'clientid'=>$client_id,
    'ses'=>$session,
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

$reviews = $result;
$array = json_decode(json_encode($reviews), true);

$can_delete = $array['can_delete'];
$name = $array['clientname'];

if ($can_delete == "true")
    $delete = "true";
else
    $delete = "false";

$backups = $array["backups"];

//Formatage de date
function secs2date($secs,$date)
{
    if ($secs>2147472000)
    {
        $date->setTimestamp(2147472000);
        $s=$secs-2147472000;
        $date->add(new DateInterval('PT'.$s.'S'));
    }
    else
        $date->setTimestamp($secs);
}

function formatBytes($bytes, $precision = 2) 
{ 
    $units = array('B', 'KB', 'MB', 'GB', 'TB'); 

    $bytes = max($bytes, 0); 
    $pow = floor(($bytes ? log($bytes) : 0) / log(1024)); 
    $pow = min($pow, count($units) - 1); 

    $bytes /= pow(1024, $pow);

    return round($bytes, $precision) . ' ' . $units[$pow]; 
}
?>
<br>
<a class='btn btn-small btn-primary' title=<?php echo _T("Start incremental backup", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=start_backup&amp;backuptype=incremental&amp;clientid=<?php echo $client_id ?>">Start incremental backup</a>
<a class='btn btn-small btn-primary' title=<?php echo _T("Start full backup", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=start_backup&amp;backuptype=full&amp;clientid=<?php echo $client_id ?>">Start full backup</a>
<br>
<br>
<label><?php echo _T("Client name: ", 'urbackup').$name; ?></label>
<br>
<h2> <?php echo _T("File save", 'urbackup'); ?> </h2>

<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr style='text-align: left;'>
          <th> <?php echo _T("Id", 'urbackup'); ?> </th>
          <th> <?php echo _T("Incremental", 'urbackup'); ?> </th>
          <th> <?php echo _T("Archived ?", 'urbackup'); ?> </th>
          <th> <?php echo _T("Time", 'urbackup'); ?> </th>
          <th> <?php echo _T("Size", 'urbackup'); ?> </th>
          <th style='text-align: right;'> <?php echo _T("Action", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>
<?php 
foreach ($backups as $backup) {
    $id_backup = $backup['id'];
    $date=new dateTime();

    if (isset($file['dir']))
        $dir = "false";
    else
        $dir = "true";

    $secs=$backup['backuptime'];
    secs2date($secs,$date);
    $dt=$date->format('Y-m-d H:i:s');

    $size = formatBytes($backup['size_bytes']);

    if ($backup['incremental'] == "0")
        $incremental = _T("No", 'urbackup');
    else
        $incremental = _T("Yes", 'urbackup');

    if ($backup['archived'] == "0")
        $archive = _T("No", 'urbackup');
    else
        $archive = _T("Yes", 'urbackup');
?>
        <tr >
            <td>
                <a href="main.php?module=urbackup&amp;submod=urbackup&amp;action=all_files_backup&amp;clientid=<?php echo $client_id; ?>&amp;backupid=<?php echo $id_backup; ?>&amp;volumename=<?php echo "/" ?>"><?php echo $backup['id']; ?></a>
            </td>
            <td> <?php echo $incremental; ?></td>
            <td> <?php echo $archive; ?></td>
            <td> <?php echo $dt; ?></td>
            <td> <?php echo $size; ?></td>
            <td>
            <ul class="action">
                <li class="display">
                    <a title=<?php echo _T("Browse", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=all_files_backup&amp;clientid=<?php echo $client_id; ?>&amp;backupid=<?php echo $id_backup; ?>&amp;volumename=<?php echo "/" ?>">&nbsp;</a>
                </li>
                <?php
                if ($delete == "true")
                {
                    if (isset($backup['disable_delete']))
                    {
                        if ($backup['disable_delete'] == "false")
                        {
                            echo '<li class="delete">';
                                echo '<a title='._T("Delete", 'urbackup').' href="main.php?module=urbackup&amp;submod=urbackup&amp;action=delete" onclick="PopupWindow(event,"main.php?module=urbackup&amp;submod=urbackup&amp;action=delete", 300); return false;">&nbsp;</a>';
                            echo '</li>';
                        }
                    }
                    else
                    {
                        echo '<li class="delete">';
                            echo '<a title='._T("Delete", 'urbackup').' href="main.php?module=urbackup&amp;submod=urbackup&amp;action=delete" onclick="PopupWindow(event,"main.php?module=urbackup&amp;submod=urbackup&amp;action=delete", 300); return false;">&nbsp;</a>';
                        echo '</li>';
                    }
                }
                ?>
            </ul>
            </td>
        </tr>
<?php
}
?>
    </tbody>
</table>