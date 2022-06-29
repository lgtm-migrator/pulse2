<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Group creation", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$users_group_array = xmlrpc_get_clients();

$groupname = $_POST['groupname'];

$group_array = $users_group_array['navitems']['groups'];

$group_already_exist = "False";

$need_name = "False";

foreach ($group_array as $group) {
    if ($group['name'] == $groupname) {
        $group_already_exist = "True";
    }
}

if ($group_already_exist == "False") 
{
    if(strlen(trim($_POST['groupname']))<=0){
        $need_name = "True";
    }
    else
    {
        $create_group = xmlrpc_add_group($groupname);
    }
}

?>
<br>
<br>
<?php
$url = 'main.php?module=urbackup&submod=urbackup&action=usersgroups&groupalreadyexist='.$group_already_exist.'&groupname='.$groupname.'&needname='.$need_name.'';

header("Location: ".$url);
?>