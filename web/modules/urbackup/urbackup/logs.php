<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Logs", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$logs_global = xmlrpc_get_logs();
$logs = $logs_global['logdata'];

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

<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr style='text-align: left;'>
          <th> <?php echo _T("Id", 'urbackup'); ?> </th>
          <th> <?php echo _T("Message", 'urbackup'); ?> </th>
          <th> <?php echo _T("Time", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>
<?php 
foreach ($logs as $log)
{
    $date=new dateTime();

    $secs=$log['time'];  //2033-12-06 08:53:20
    secs2date($secs,$date);
    $dt=$date->format('Y-m-d H:i:s');
?>
        <tr >
            <td> <?php echo $log['id']; ?></td>
            <td> <?php echo $log['msg']; ?></td>
            <td> <?php echo $dt; ?></td>
        </tr>
<?php
}
?>
    </tbody>
</table>