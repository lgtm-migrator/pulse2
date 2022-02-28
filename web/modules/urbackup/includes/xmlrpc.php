<?php
function xmlrpc_tests(){
    // Return the element of the urbackup.tests table.
    return xmlCall("urbackup.tests", array());
}

function xmlrpc_login(){
    // Return the login parameters from urbackup api
    return xmlCall("urbackup.login", []);
}

function xmlrpc_get_session(){
    // Return the session token
    return xmlCall("urbackup.get_ses", []);
}

function xmlrpc_get_logs(){
    // Return logs for all user
    return xmlCall("urbackup.get_logs", []);
}

function xmlrpc_add_client($clientname){
    // Return logs for all user
    return xmlCall("urbackup.add_client", [$clientname]);
}

function xmlrpc_check_client($jidmachine, $clientid, $authkey){
    // 
    return xmlCall("urbackup.check_client", [$jidmachine, $clientid, $authkey]);
}

function xmlrpc_get_settings_global(){
    // Return all settings
    return xmlCall("urbackup.get_settings_general", []);
}

function xmlrpc_get_clients(){
    // Return all user
    return xmlCall("urbackup.get_settings_clients", []);
}

function xmlrpc_get_backups_all_client(){
    // Return backups of all clients with date last backup
    return xmlCall("urbackup.get_backups_all_client", []);
}

function xmlrpc_get_backups_for_client($client_id){
    // Return backups of one clients with date last backup
    return xmlCall("urbackup.get_backups_for_client", [$client_id]);
}

function xmlrpc_get_backup_files($client_id, $backup_id, $path){
    // List file for of backup, need path
    return xmlCall("urbackup.get_backup_files", [$client_id, $backup_id, $path]);
}

function xmlrpc_client_download_backup_file($client_id, $backup_id, $path, $filter){
    // Restore file for client
    return xmlCall("urbackup.client_download_backup_file", [$client_id, $backup_id, $path, $filter]);
}

function xmlrpc_client_download_backup_file_shahash($client_id, $backup_id, $path, $shahash){
    // Restore file for client, need shahash for only file
    return xmlCall("urbackup.client_download_backup_file_shahash", [$client_id, $backup_id, $path, $shahash]);
}

function xmlrpc_get_status(){
    // Return status
    return xmlCall("urbackup.get_status", []);
}

function xmlrpc_get_progress(){
    // Return progress
    return xmlCall("urbackup.get_progress", []);
}

function xmlrpc_create_backup_incremental_file($client_id){
    // Return state for incremental save of file
    return xmlCall("urbackup.create_backup_incremental_file", [$client_id]);
}

function xmlrpc_create_backup_full_file($client_id){
    // Return Return state for full save of file
    return xmlCall("urbackup.create_backup_full_file", [$client_id]);
}

function xmlrpc_get_status_client($clientname){
    // Return status
    return xmlCall("urbackup.get_status_client", [$clientname]);
}
?>
