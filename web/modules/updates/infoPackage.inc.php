<?php
require_once("modules/pulse2/version.php");

$mod = new Module("updates");
$mod->setVersion("1.0");
//$mod->setRevision('');
$mod->setDescription(_T("Updates", "updates"));
$mod->setAPIVersion("1:0:0");
$mod->setPriority(2000);

$submod = new SubModule("updates");
$submod->setDescription(_T("Updates", "updates"));
$submod->setVisibility(True);
$submod->setImg('modules/updates/graph/navbar/updates');
$submod->setDefaultPage("updates/updates/index");
$submod->setPriority(500);

$page = new Page("index", _T('Page de tests', 'updates'));
$page->setFile("modules/updates/updates/index.php");
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod); ?>

