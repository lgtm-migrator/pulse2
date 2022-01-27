<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Saves", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$backups_list_array = xmlrpc_get_backups_all_client();
$clients_backup_list = $backups_list_array["clients"];

$client_array = xmlrpc_get_status();
$clients = $client_array["status"];

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


<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr style='text-align: left;'>
            <th> <?php echo _T("Clients name", 'urbackup'); ?> </th>
            <th> <?php echo _T("Last backup file", 'urbackup'); ?> </th>
            <th> <?php echo _T("Action", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>

<?php
foreach ($clients_backup_list as $client_backup) {
    $id = $client_backup['id'];
    $date=new dateTime();

    $secs=$client_backup['lastbackup'];  //2033-12-06 08:53:20
    secs2date($secs,$date);
    $dt=$date->format('Y-m-d H:i:s');

?>
        <tr class="alternate">
            <td style='padding:0px 500px 0px 5px;'>
                <a href="main.php?module=urbackup&amp;submod=urbackup&amp;action=list_backups&amp;clientid=<?php echo $id; ?>"><?php echo $client_backup['name']; ?></a>
            </td>
            <td> <?php echo $dt; ?></td>
            <td>
            <li class="display">
                <a title=<?php echo _T("Browse", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=list_backups&amp;clientid=<?php echo $id; ?>">&nbsp;</a>
            </li>
            </td>
        </tr>
<?php
}
?>

    </tbody>
</table>
