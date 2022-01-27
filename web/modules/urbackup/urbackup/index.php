<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Reviews", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$ini_array = parse_ini_file("/etc/mmc/plugins/urbackup.ini");
$username_urbackup = $ini_array['username'];
$password_urbackup = $ini_array['password'];

function formatBytes($bytes, $precision = 2)
{ 
    $units = array('B', 'KB', 'MB', 'GB', 'TB'); 

    $bytes = max($bytes, 0); 
    $pow = floor(($bytes ? log($bytes) : 0) / log(1024)); 
    $pow = min($pow, count($units) - 1); 

    $bytes /= pow(1024, $pow);

    return round($bytes, $precision) . ' ' . $units[$pow]; 
}

//Formatage de date
function secs2date($secs,$date)
{
    if ($secs>2147472000)    //2038-01-19 expire dt
    {
        $date->setTimestamp(2147472000);
        $s=$secs-2147472000;
        $date->add(new DateInterval('PT'.$s.'S'));
    }
    else
        $date->setTimestamp($secs);
}

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

//-----------------------------------START GET_PROGRESS FUNCTION
$url = "https://wva.siveo.net/urbackup/x?a=progress";
$curlid = curl_init($url);

curl_setopt($curlid, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curlid, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curlid, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curlid, CURLOPT_POST, true);
curl_setopt($curlid, CURLOPT_RETURNTRANSFER, true);

$datas = [
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

$reviews = $result["lastacts"];
$array = json_decode(json_encode($reviews), true);
//-----------------------------------END GET_PROGRESS

?>
<br>
<br>
<h2><?php echo _T("Last activities", 'urbackup'); ?></h2>
<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr style='text-align: left;'>
          <th> <?php echo _T("Id", 'urbackup'); ?> </th>
          <th> <?php echo _T("Name", 'urbackup'); ?> </th>
          <th> <?php echo _T("Backuptime", 'urbackup'); ?> </th>
          <th> <?php echo _T("Status", 'urbackup'); ?> </th>
          <th> <?php echo _T("Duration H:M:S", 'urbackup'); ?> </th>
          <th> <?php echo _T("Size", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>
<?php
foreach ($array as $review) {
    if ($review['del'] == 'true')
    {
        if ($review['image'] == '1')
            $status = "Delete of full Disk Image";
        
        if ($review['incremental'] != '0')
            $status = "Delete of incremental save";
    }
    else
    {
        if ($review['image'] != '0')
            $status = 'Disk Image';
        else
            $status = 'Incremental Save';
    }

    if ($review['restore'] != '0')
    {
        if ($review['image'] == '1')
            $status = "Restoration of full Disk Image";
        
        if ($review['incremental'] != '0')
            $status = "Restoration of incremental save";
    }

    $size = formatBytes($review['size_bytes']);
    $duration = $review['duration'];
    $duration = $duration*10;
    $duration = $duration." seconds";

    $seconds = round($duration);
 
    $output_duration = sprintf('%02d:%02d:%02d', ($seconds/ 3600),($seconds/ 60 % 60), $seconds% 60);

    $date=new dateTime();

    $secs=$review['backuptime'];
    secs2date($secs,$date);
    $dt=$date->format('Y-m-d H:i:s');
?>
        <tr>
            <td style='padding-left: 5px;'> <?php echo $review['id']; ?></td>
            <td> <?php echo $review['name']; ?></td>
            <td> <?php echo $dt; ?></td>       
            <td> <?php echo $status; ?></td>
            <td> <?php echo $output_duration; ?></td>
            <td> <?php echo $size; ?></td>
        </tr>
<?php
}
?>
    </tbody>
</table>
