<?
/**
 * (c) 2020 Siveo, http://siveo.net
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

$sidemenu= new SideMenu();
$sidemenu->setClass("urbackup");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Clients machine list", 'urbackup'), "urbackup", "urbackup", "index"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Download Windows client", 'urbackup'), "urbackup", "urbackup", "downloads_client_urb"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Saves", 'urbackup'), "urbackup", "urbackup", "saves"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Users and groups list", 'urbackup'), "urbackup", "urbackup", "usersgroups"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Settings", 'urbackup'), "urbackup", "urbackup", "settings"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Review", 'urbackup'), "urbackup", "urbackup", "review"));
?>