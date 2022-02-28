<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Groups", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$users_group_array = xmlrpc_get_clients();
?>

<br>
<br>
<h1><?php echo _T("Create group :", "urbackup"); ?></h1>
<br>
<form action="main.php?module=urbackup&amp;submod=urbackup&amp;action=create_group" method="POST">
    <label>Group name :</label><input type="text" name="groupname" id="groupname"/>
    <input type="submit" value="Create groupe">
</form>

<br>
<br>

<?php
$group_array = $users_group_array['navitems']['groups'];
?>

<h1> <?php echo _T("Groups list :", 'urbackup'); ?> </h1>
<br>
<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr>
            <th style='text-align: left;'> <?php echo _T("Group name", 'urbackup'); ?> </th>
            <th style='text-align: right;'> <?php echo _T("Actions", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>
<?php
foreach ($group_array as $group) {
    if ($group['name'] != "") {
?>
        <tr>
            <td style='padding-left: 5px;'> <?php echo $group['name']; ?></td>
            <td>
            <ul class="action">
                <li class="edit">
                    <a title=<?php echo _T("Edit", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=edit_group_settings&amp;groupid=<?php echo $group['id']; ?>&amp;groupname=<?php echo $group['name']; ?>">&nbsp;</a>
                </li>
                <li class="delete">
                    <a title=<?php echo _T("Delete", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=delete" onclick="PopupWindow(event,'main.php?module=urbackup&amp;submod=urbackup&amp;action=delete', 300); return false;">&nbsp;</a>
                </li>
            </ul>
            </td>
        </tr>
<?php
    }
}
?>
    </tbody>
</table>
