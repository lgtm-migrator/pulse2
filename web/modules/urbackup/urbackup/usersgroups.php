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
<table style:'border: 1px solid #333;'>
    <thead>
        <tr>
            <th colspan="2"> <?php echo _T("User list", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style='text-align: left; text-decoration: underline;'> <?php echo _T("User name", 'urbackup'); ?> </td>
            <td style='text-align: left; text-decoration: underline;'> <?php echo _T("Rights", 'urbackup'); ?> </td>
        </tr>

<?php
$user_array = $users_group_array['users'];

foreach ($user_array as $user) {
?>
        <tr>
            <td> <?php echo $user['name']; ?></td>
            <td>
            <?php
            $user_rights = $user['rights'];

            foreach ($user_rights as $rights) {
                  echo $rights['domain'].': '.$rights['right'].'. ';
            }
            ?>
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
<table style:'border: 1px solid #333;'>
    <thead>
        <tr>
            <th colspan="2"> <?php echo _T("Group list", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style='text-align: left; text-decoration: underline;'> <?php echo _T("Group name", 'urbackup'); ?> </td>
        </tr>
<?php
foreach ($group_array as $group) {
    if ($group['name'] != "") {
?>
        <tr>
            <td> <?php echo $group['name']; ?></td>
        </tr>
<?php
    }
}
?>
    </tbody>
<<<<<<< HEAD
</table>
=======
</table>
>>>>>>> origin/urbackup
