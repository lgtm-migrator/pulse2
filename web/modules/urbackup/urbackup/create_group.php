<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Group creation", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$groupname = $_POST['groupname'];

$create_group = xmlrpc_add_group($groupname);

?>
<br>
<br>
<?php
$url = 'main.php?module=urbackup&submod=urbackup&action=usersgroups';

header("Location: ".$url);
?>