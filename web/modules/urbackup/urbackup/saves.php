<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Saves", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$backups_list_array = xmlrpc_get_backups();
$clients_backup_list = $backups_list_array["clients"];
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
?>
        <tr>
            <td style='padding:0px 500px 0px 0px;'> <?php echo $client_backup['name']; ?></td>
            <td> <?php echo $client_backup['lastbackup']; ?></td>
        </tr>
<?php
}
?>

    </tbody>
</table>
