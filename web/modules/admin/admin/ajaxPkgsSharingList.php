<?php
/**
 * (c) 2021 Siveo, http://siveo.net
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

require_once("modules/pkgs/includes/xmlrpc.php");

$filter = isset($_GET['filter']) ? $_GET['filter'] : "";
$maxperpage = isset($_GET['maxperpage']) ? (int)$_GET['maxperpage'] : -1;
$start = isset($_GET['start']) ? (int)$_GET['start'] : 0;

$shares = get_shares_list($start, $maxperpage, $filter);
$total = $shares['total'];
$datas = [
  'usedquotas'=> [],
  'share_path'=> [],
  'uri'=> [],
  'id'=> [],
  'Ars_id'=> [],
  'ars_name'=> [],
  'name'=> [],
  'enabled'=> [],
  'quotas' => [],
  'comments' => [],
  'type' => []
];
foreach($shares['datas'] as $key => $share){
  $datas['usedquotas'][] = $share['usedquotas'];
  $datas['share_path'][] = $share['share_path'];
  $datas['uri'][] = $share['uri'];
  $datas['id'][] = $share['id'];
  $datas['Ars_id'][] = $share['Ars_id'];
  $datas['ars_name'][] = $share['ars_name'];
  $datas['name'][] = $share['name'];
  $datas['enabled'][] = $share['enabled'];
  $datas['quotas'][] = $share['quotas'];
  $datas['comments'][] = $share['comments'];
  $datas['type'][] = $share['type'];
}

$n = new OptimizedListInfos( $datas['name'], _T("Share Name", "pkgs"));
$n->addExtraInfo( $datas['comments'], _T("Comment", "pkgs"));
$n->addExtraInfo( $datas['type'], _T("Type", "pkgs"));
$n->addExtraInfo( $datas['enabled'], _T("Enabled", "pkgs"));
$n->addExtraInfo($datas['ars_name'], _T("Relay", "pkgs"));
$n->addExtraInfo($datas['share_path'], _T("Path", "pkgs"));
//$n->addActionItemArray($datas['ars_name'], _T("Relay", "pkgs"));
$n->setItemCount($shares['total']);
$n->setNavBar(new AjaxNavBar($shares['total'], $filter));

//$n->setParamInfo($shares['datas']);
$n->start = 0;
$n->end = $shares['total'];

$n->display();
?>
