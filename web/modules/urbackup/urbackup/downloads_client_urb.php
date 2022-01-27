<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Download page of Urbackup Client", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();
$windows_link = "https://hndl.urbackup.org/Client/2.4.11/UrBackup%20Client%202.4.11.exe";
?>

<br>

<h2> <?php echo _T("Windows client", 'urbackup'); ?> </h2>
<?php echo "<button><a href='$windows_link' target='_blank'>Download</a></button>"; ?>

<br>
<br>

<h2> <?php echo _T("Linux clients", 'urbackup'); ?> </h2>
<p> <?php echo _T("Run command :", 'urbackup'); ?> </p>

<p>TF=$(mktemp) && wget "https://hndl.urbackup.org/Client/2.4.11/UrBackup%20Client%20Linux%202.4.11.sh" -O $TF && sudo sh $TF; rm -f $TF</p>