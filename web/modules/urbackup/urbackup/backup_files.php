<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("List Backups by Client", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$client_id = htmlspecialchars($_GET["clientid"]);
$backup_id = htmlspecialchars($_GET["backupid"]);

$backup_files = xmlrpc_get_backup_files($client_id, $backup_id);
$files = $backup_files['files'];
$client_id = $backup_files['clientid'];

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
<label><?php echo _T("Client name: ", 'urbackup').$backup_files['clientname']; ?></label>
<br>

<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr style='text-align: left;'>
          <th> <?php echo _T("Volume", 'urbackup'); ?> </th>
          <th> <?php echo _T("Size", 'urbackup'); ?> </th>
          <th> <?php echo _T("Create date", 'urbackup'); ?> </th>
          <th> <?php echo _T("Last modification", 'urbackup'); ?> </th>
          <th> <?php echo _T("Last access", 'urbackup'); ?> </th>
          <th style='text-align: right;'> <?php echo _T("Action", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>

<?php
foreach ($files as $file) 
{
    $volume_name = $file['name'];
    $date=new dateTime();

    $secs=$file['creat'];  //2033-12-06 08:53:20
    secs2date($secs,$date);
    $create_date=$date->format('Y-m-d H:i:s');

    $secs=$file['access'];  //2033-12-06 08:53:20
    secs2date($secs,$date);
    $access_date=$date->format('Y-m-d H:i:s');

    $secs=$file['mod'];  //2033-12-06 08:53:20
    secs2date($secs,$date);
    $mod_date=$date->format('Y-m-d H:i:s');


    if (isset($file['size']))
        $size = formatBytes($file['size']);
    else
        $size = "";
    
?>
        <tr >
            <td>
                <a href="main.php?module=urbackup&amp;submod=urbackup&amp;action=all_files_backup&amp;clientid=<?php echo $client_id; ?>&amp;backupid=<?php echo $backup_id; ?>&amp;volumename=<?php echo "/".$volume_name; ?>"><?php echo $file['name']; ?></a>
            </td>
            <td> <?php echo $size; ?></td>
            <td> <?php echo $create_date; ?></td>
            <td> <?php echo $mod_date; ?></td>
            <td> <?php echo $access_date; ?></td>
            <td>
            <ul class="action">
                <li class="display">
                    <a title=<?php echo _T("Browse", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=all_files_backup&amp;clientid=<?php echo $client_id; ?>&amp;backupid=<?php echo $backup_id; ?>&amp;volumename=<?php echo "/".$volume_name; ?>">&nbsp;</a>
                </li>
                <a class='btn btn-small btn-primary' title=<?php echo _T("DOWNLOAD", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=download_file&amp;timestamp=<?php echo $nowtime; ?>&amp;clientname=<?php echo $client_name; ?>&amp;clientid=<?php echo $client_id; ?>&amp;backupid=<?php echo $backup_id; ?>&amp;volumename=<?php echo $final_path; ?>&amp;filename=<?php echo $file['name'] ?>">Download</a>
                <a class='btn btn-small btn-primary' title=<?php echo _T("RESTORE", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=restore_file&amp;clientid=<?php echo $client_id; ?>&amp;backupid=<?php echo $backup_id; ?>&amp;volumename=<?php echo $final_path; ?>&amp;shahash=<?php echo $shahash; ?>">Restore</a>
            </ul>
            </td>
        </tr>
<?php
}
?>
    </tbody>
</table>