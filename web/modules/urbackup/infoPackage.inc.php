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

$page = new Page("index", _T('Review', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/index.php");
$submod->addPage($page);

$page = new Page("list_backups", _T('List Backups by Client', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/list_backups.php");
$submod->addPage($page);

$page = new Page("start_backup", _T('Start backup', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/start_backup.php");
$submod->addPage($page);

$page = new Page("checkMachine", _T('Check machine if exist', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/checkMachine.php");
$submod->addPage($page);

$page = new Page("create_group", _T('Create group', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/create_group.php");
$submod->addPage($page);

$page = new Page("add_member_togroup", _T('Assign member to group', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/add_member_togroup.php");
$submod->addPage($page);

$page = new Page("add_member_togroup_aftercheck", _T('Assign member to group after add client', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/add_member_togroup_aftercheck.php");
$submod->addPage($page);

$page = new Page("edit_group_settings", _T('Edit group', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/edit_group_settings.php");
$submod->addPage($page);

$page = new Page("list_computers_ongroup", _T('List computer on group', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/list_computers_ongroup.php");
$submod->addPage($page);

$page = new Page("validate_edit_group", _T('Validate save settings', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/validate_edit_group.php");
$submod->addPage($page);

$page = new Page("deleting_backup", _T('Delete backup', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/deleting_backup.php");
$submod->addPage($page);

$page = new Page("deleting_group", _T('Delete group', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/deleting_group.php");
$submod->addPage($page);

$page = new Page("all_files_backup", _T('List of files from on backup', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/all_files_backup.php");
$submod->addPage($page);

$page = new Page("restore_file", _T('Restore file', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/restore_file.php");
$submod->addPage($page);

$page = new Page("download_file", _T('Download file', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/download_file.php");
$submod->addPage($page);

$page = new Page("usersgroups", _T('Profiles', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/usersgroups.php");
$submod->addPage($page);

$page = new Page("logs", _T('Logs', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/logs.php");
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod); ?>