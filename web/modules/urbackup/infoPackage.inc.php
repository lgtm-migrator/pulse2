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

$page = new Page("index", _T('Client machine list', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/index.php");
$submod->addPage($page);

$page = new Page("saves", _T('Saves', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/saves.php");
$submod->addPage($page);

$page = new Page("list_backups", _T('List Backups by Client', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/list_backups.php");
$submod->addPage($page);

$page = new Page("backup_files", _T('List of file on backup', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/backup_files.php");
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

$page = new Page("usersgroups", _T('Users and groups list', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/usersgroups.php");
$submod->addPage($page);

$page = new Page("settings", _T('Settings', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/settings.php");
$submod->addPage($page);

$page = new Page("review", _T('Review', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/review.php");
$submod->addPage($page);

$page = new Page("logs", _T('Logs', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/logs.php");
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod); ?>
