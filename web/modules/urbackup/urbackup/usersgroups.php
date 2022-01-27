<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Users and groups list", 'pkgs'));
$p->setSideMenu($sidemenu);
$p->display();

$users_group_array = xmlrpc_get_clients();
?>

<br>
<br>
<h2> <?php echo _T("Users list :", 'urbackup'); ?> </h2>
<br>
<br>
<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr>
            <th style='text-align: left;'> <?php echo _T("User name", 'urbackup'); ?> </th>
            <th style='text-align: left;'> <?php echo _T("Rights", 'urbackup'); ?> </th>
            <th style='text-align: right;'> <?php echo _T("Actions", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>

<?php
$user_array = $users_group_array['users'];

foreach ($user_array as $user) {
?>
        <tr>
            <td style='padding-left: 5px;'> <?php echo $user['name']; ?></td>
            <td>
            <?php
            $user_rights = $user['rights'];

            foreach ($user_rights as $rights) {
                  echo $rights['domain'].': '.$rights['right'].'. ';
            }
            ?>
            </td>
            <td>
            <ul class="action">
                <li class="delete">
                    <a title=<?php echo _T("Delete", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=delete" onclick="PopupWindow(event,'main.php?module=urbackup&amp;submod=urbackup&amp;action=delete', 300); return false;">&nbsp;</a>
                </li>
            </ul>
            </td>
        </tr>
<?php
}
?>
    </tbody>
</table>
<br>
<br>

<?php
$group_array = $users_group_array['navitems']['groups'];
?>

<h2> <?php echo _T("Groups list :", 'urbackup'); ?> </h2>
<br>
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
