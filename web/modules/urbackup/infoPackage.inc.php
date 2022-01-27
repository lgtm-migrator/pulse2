<?php
require_once("modules/pulse2/version.php");

$mod = new Module("urbackup");
$mod->setVersion("1.0");
//$mod->setRevision('');
$mod->setDescription(_T("Urbackup", "urbackup"));
$mod->setAPIVersion("1:0:0");
$mod->setPriority(2000);

$submod = new SubModule("urbackup");
$submod->setDescription(_T("Urbackup", "urbackup"));
$submod->setVisibility(True);
$submod->setImg('modules/urbackup/graph/navbar/urbackup');
$submod->setDefaultPage("urbackup/urbackup/index");
$submod->setPriority(500);

$page = new Page("index", _T('Liste des clients machine', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/index.php");
$submod->addPage($page);

$page = new Page("downloads_client_urb", _T('Téléchargement client Windows', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/downloads_client_urb.php");
$submod->addPage($page);

$page = new Page("activities", _T('Activités', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/activities.php");
$submod->addPage($page);

$page = new Page("usersgroups", _T('UsersGroups', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/usersgroups.php");
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod); ?>
