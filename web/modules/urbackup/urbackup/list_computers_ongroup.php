
<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$group_id = htmlspecialchars($_GET["groupid"]);
$group_name = htmlspecialchars($_GET["groupname"]);

$p = new PageGenerator(_T("List user on profil ".$group_name, 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$clients = xmlrpc_get_backups_all_client();

$ini_array = parse_ini_file("/etc/mmc/plugins/urbackup.ini");
$username_urbackup = $ini_array['username'];
$password_urbackup = $ini_array['password'];
$url_urbackup = $ini_array['url'];

//-----------------------------------START LOGIN FUNCTION
$url = $url_urbackup."?a=login";

$curlid = curl_init($url);

curl_setopt($curlid, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curlid, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curlid, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curlid, CURLOPT_POST, true);
curl_setopt($curlid, CURLOPT_RETURNTRANSFER, true);
$datas = [
'username'=>$username_urbackup,
'password'=>$password_urbackup,
'plainpw'=>1
];

$urlencoded = "";
foreach($datas as $key=>$val){
$urlencoded .= $key.'='.$val.'&';
}
rtrim($urlencoded, '&');

curl_setopt($curlid, CURLOPT_POSTFIELDS, $urlencoded);
$response = curl_exec($curlid);

if (curl_errno($curlid)) 
{
    echo 'Requête échouée : '.curl_error($curlid).'<br>';
    $result = [];
}
else
{
$result = (array)json_decode($response);
}

curl_close($curlid);

if(isset($result['session'], $result['success']) && $result['success'] == 1){
    $session = $result['session'];
}
//-----------------------------------END LOGIN

//-----------------------------------START SAVE SETTINGS FUNCTION
$url = $url_urbackup."?a=settings";
$curlid = curl_init($url);

curl_setopt($curlid, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curlid, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curlid, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curlid, CURLOPT_POST, true);
curl_setopt($curlid, CURLOPT_RETURNTRANSFER, true);

$datas = [
    'sa'=>'general',
    'ses'=>$session,
];

$urlencoded = "";
foreach($datas as $key=>$val){
$urlencoded .= $key.'='.$val.'&';
}
rtrim($urlencoded, '&');

curl_setopt($curlid, CURLOPT_POSTFIELDS, $urlencoded);
$response = curl_exec($curlid);

$result = (array)json_decode($response);

curl_close($curlid);

$settings = $result;
$array = json_decode(json_encode($settings), true);

$clients = $array['navitems']['clients'];
//-----------------------------------END SAVE SETTINGS

?>
<br>
<h2><?php echo _T("Add member to this group", 'urbackup'); ?></h2>
<br>
<form name="form" action="main.php?module=urbackup&amp;submod=urbackup&amp;action=add_member_togroup&amp;groupname=<?php echo $group_name; ?>&amp;groupid=<?php echo $group_id; ?>" method="post">
    <select name="client">
        <?php
        foreach($clients as $client)
        {
            echo '<option id="clientid" name="clientid" value="'.$client['id'].'">'.$client['name'].'</option>';
        }
        ?>
    </select>
    <input type="submit" name="subadd" id="subadd" value="Add this member">
</form>
<br>
<br>
<div style="display:flex">
    <div>
        <h3>Computer <b>outside</b> the profil</h3>
        <ul id="outProfil" name="outProfil" class="ui-sortable" style="background-color: white; width: 250px; height: 200px; padding-top: 10px; margin-right: 30px;">
            <?php
            foreach($clients as $client)
            {
                if ($client['group'] != $group_id)
                {
                    echo "<li value=".$client['id']." class='ui-draggable ui-draggable-handle ui-sortable-handle' style='width: 250px; height: 14px;'>".$client['name']."</li>";
                }
            }
            ?>
        </ul>
    </div>
    <div>
        <h3>Computer <b>inside</b> the profil</h3>
        <ul id="inProfil" name="inProfil" class="ui-sortable" style="background-color: white; width: 250px; height: 200px; padding-top: 10px;">
            <?php
            foreach($clients as $client)
            {
                if ($client['group'] == $group_id)
                {
                    echo "<li value=".$client['id']." class='ui-draggable ui-draggable-handle ui-sortable-handle' style='width: 250px; height: 14px;'>".$client['name']."</li>";
                }
            }
            ?>
        </ul>
    </div>
</div>

<script>
jQuery(function(){
  jQuery("#outProfil li, #inProfil li").draggable({
    connectToSortable: "#inProfil, #outProfil",
    stop: function(){
      profil_list = []
      profil_id = []

      jQuery("#inProfil li").each(function(id, idgroup){
            //
            <?php
            $url = "main.php?module=urbackup&amp;submod=urbackup&amp;action=add_member_togroup&amp;groupname=".$group_name."&amp;groupid=".$group_id."&amp;clientid=".$clientid;
            //header("Location: ".$url);
            ?>
      })

      jQuery("input[name='relays_id']").val(profil_id.join(','))
      jQuery("input[name='relays_list']").val(profil_list.join(','))
    },
  })

  jQuery( "#outProfil, #inProfil" ).sortable({
    revert: true
  });
  jQuery( "ul, li" ).disableSelection();
});
</script>