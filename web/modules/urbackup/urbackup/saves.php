<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Saves", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$backups_list_array = xmlrpc_get_backups();
$clients_backup_list = $backups_list_array["clients"];

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

?>

<br>

<table style:'border: 1px solid #333;'>
    <thead>
        <tr style='text-align: left; text-decoration: underline;'>
            <th> <?php echo _T("Clients name", 'urbackup'); ?> </th>
            <th> <?php echo _T("Last backup file", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>

<?php
foreach ($clients_backup_list as $client_backup) {

    $date=new dateTime();

    $secs=$client_backup['lastbackup'];  //2033-12-06 08:53:20
    secs2date($secs,$date);
    $dt=$date->format('Y-m-d H:i:s');

?>
        <tr>
            <td style='padding:0px 500px 0px 0px;'> <?php echo $client_backup['name']; ?></td>
            <td> <?php echo $dt; ?></td>
        </tr>
<?php
}
?>

    </tbody>
</table>
