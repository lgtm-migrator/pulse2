<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$group_id = htmlspecialchars($_GET["groupid"]);
$group_name = htmlspecialchars($_GET["groupname"]);

$p = new PageGenerator(_T("Settings for ".$group_name, 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

?>
<br>
<form action="main.php?module=urbackup&amp;submod=urbackup&amp;action=validate_edit_group&amp;groupid=<?php echo $group_id; ?>" method="POST">
    <label><?php echo _T("Interval for incremental file backups", "urbackup"); ?></label><input type="text" name="update_freq_incr" id="update_freq_incr"/>
    <label><?php echo _T("Interval for full file backups", "urbackup"); ?></label><input type="text" name="update_freq_full" id="update_freq_full"/>
    <label><?php echo _T("Excluded files", "urbackup"); ?></label><input type="text" name="exclude_files" id="exclude_files"/>
    <label><?php echo _T("Included files", "urbackup"); ?></label><input type="text" name="include_files" id="include_files"/>
    <label><?php echo _T("Default directories to backup", "urbackup"); ?></label><input type="text" name="default_dirs" id="default_dirs"/>
    <input type="submit" value="Save">
</form>