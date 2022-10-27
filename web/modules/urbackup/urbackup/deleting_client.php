<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$clientname = htmlspecialchars($_GET["clientname"]);
$jidMachine = htmlspecialchars($_GET["jidmachine"]);

$p = new PageGenerator(_T("Delete client", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

#au niveau du client
# set backup_enable to 0 too
$client_remove = xmlrpc_remove_client($jidMachine);

?>
<br>
<p><?php echo _T("Every backup type has been disable for this client (cannot be removed from interface).","urbackup"); ?></p>
<br>
<a class='btn btn-small btn-primary' title=<?php echo _T("Back to computer view", 'urbackup'); ?> href="main.php?module=base&amp;submod=computers&amp;action=machinesList"><?php echo _T("Back to computer view", 'urbackup'); ?></a>