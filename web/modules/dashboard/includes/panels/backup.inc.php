<?php
/*
 * (c) 2016 siveo, http://www.siveo.net/
 *
 * This file is part of Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

include_once("modules/dashboard/includes/panel.class.php");
require_once("modules/backuppc/includes/xmlrpc.php");

$options = array(
    "class" => "BackupPanel",
    "id" => "backup",
    "title" => _T("Machines backup", "dashboard"),
    "enable" => true,
);

class BackupPanel extends Panel {

    function display_content() {
        $urlRedirect = urlStrRedirect("base/computers/createBackupStaticGroup");
        $total_machines = getComputerCount();
        $machines_backup = get_count_of_backuped_hosts();
        $machines_not_backup = $total_machines - $machines_backup;
        echo _T("Total machines : ") .$total_machines.'<br/>';
        echo '<span style="color:green">' . _T("Backup configured : ", "dashboard") . $machines_backup.'</span><a href="'.$urlRedirect.'&backup=yes"><img title="'._T("Create a group","dashboard").'" style="height: 10px; padding-left: 3px;" src="img/machines/icn_machinesList.gif" /></a><br/>';
        echo '<span style="color:red">' . _T("Backup not configured : ", "dashboard") .$machines_not_backup.'</span><a href="'.$urlRedirect.'&backup=no"><img title="'._T("Create a group","dashboard").'" style="height: 10px; padding-left: 3px;" src="img/machines/icn_machinesList.gif" /></a><br/>';
    }
}
?>
