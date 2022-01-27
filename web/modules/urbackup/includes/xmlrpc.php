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

function xmlrpc_get_settings_global(){
    // Return all settings
    return xmlCall("urbackup.get_settings", []);
}

function xmlrpc_get_clients(){
    // Return all user
    return xmlCall("urbackup.get_clients", []);
}

function xmlrpc_get_backups(){
    // Return backups of all clients with date last backup
    return xmlCall("urbackup.get_backups", []);
}

function xmlrpc_get_status(){
    // Return status
    return xmlCall("urbackup.get_status", []);
}

/*function xmlrpc_get_status_client($clientname){
    // Return status
    return xmlCall("urbackup.get_status_client", [$clientname]);
}*/
?>
