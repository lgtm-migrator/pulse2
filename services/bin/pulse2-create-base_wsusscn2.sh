#!/bin/bash
#
# (c) siveo, http://siveo.net
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

# ############################
# GENERATION DE LA BASE script a executer depuis crontab en nohuo redirections des sortie vers /log/generetionwsu.log  descripteur "0 2 * * *"
# ############################
####  A faire creation du fichier pulse2-create-base_wsusscn2.ini
###   par exemple
conffileinit="/etc/pulse2-create-base_wsusscn2/pulse2-create-base_wsusscn2.init"


######## ----------------  CONTENU FICHIER DE CONF A ADAPTER
## connection base_wsusscn2
#[connection]
#host=localhost       -----------> a adapter
#user=jfk             -----------> a adapter
#port=3360            -----------> a adapter
#password=jfk         -----------> a adapter

#[main]
#NAME_BASE=base_wsusscn2
#NAME_TABLE=update_data
#NAME_UPDATE_TABLE=data_simple_update
#directory_output = /media/jfk/TOSHIBA EXT/winupdatetst         -----------> a adapter
#name_file_wsu=wsusscn2.cab
#url=http://go.microsoft.com/fwlink/?linkid=74689
#[generation_package]
#directory_output_package = /media/jfk/TOSHIBA EXT/winupdate/update_packages        -----------> a adapter
#######---------


conffileinit="/etc/pulse2-create-base_wsusscn2/pulse2-create-base_wsusscn2.init"



user="jfk"
password="jfk"
database="base_wsusscn2"
host="localhost"
url="http://go.microsoft.com/fwlink/p/?LinkID=74689"
user=$(crudini --get $conffileinit "connection" "user")
password=$(crudini --get $conffileinit "connection" "password")
host=$(crudini --get $conffileinit "connection" "host")
database=$(crudini --get $conffileinit "main" "NAME_BASE")
url=$(crudini --get $conffileinit "main" "url")
directory_output=$(crudini --get $conffileinit "main" "directory_output")
name_file_wsu=$(crudini --get $conffileinit "main" "name_file_wsu")

echo $user
echo $database
echo $host
echo $url
echo $directory_output
echo $name_file_wsu



path_base_wsusscn2_md5="/var/script_generateur_de_base/wsusscn2.md5"
path_base_wsusscn2_dump="/var/script_generateur_de_base/webfile/dumptable_update_data.sql"
path_base_wsusscn2="/usr/sbin/script_base_wsusscn22.sql"
path_tmp_file="/tmp/$name_file_wsu"

suffixe="__save"

function table_exists() { table=$(echo "show tables from base_wsusscn2 like '$1';" | mysql -N --user=$user --password=$password); if [[ -n "$table" ]]; then  echo "1"; else echo "0";  fi; }

function droptable(){
echo "DROP DATABASE IF EXISTS $1;"
    mysql --user="$user" --password="$password" --database="$database" --execute="DROP DATABASE IF EXISTS $1;"
}

function rename_table(){
echo "ALTER TABLE \`$database\`.\`$1\` RENAME TO  \`$database\`.\`$2\`;"
mysql --user="$user" --password="$password" --database="$database" --execute="ALTER TABLE \`$database\`.\`$1\` RENAME TO  \`$database\`.\`$2\`;"
}


# on download le fichier
if ! wget -o /dev/null -O $path_tmp_file $url
then
    echo 'download to $path_tmp_file error'
    exit -1
else
    echo "download to $path_tmp_file succes"
    md5=$(md5sum $path_tmp_file | cut -d' ' -f1)
    echo "md5 file $path_tmp_file is $md5"
fi

# > $path_base_wsusscn2_md5
echo "test if $path_base_wsusscn2_md5 exist"
if [ -f $path_base_wsusscn2_md5 ]
then
    echo "il exits old_md5  $path_base_wsusscn2_md5"
else
    echo "il exits pas old_md5  $path_base_wsusscn2_md5"
    #sauve md5
    echo $md5 > $path_base_wsusscn2_md5
    # on attribut 1 md5 faux
    md5=$(echo "md5_non_valable")
fi
echo "MD5 is" $md5

oldmd5=$(cat $path_base_wsusscn2_md5)


# on compare md( avc oldmd5
if [ "x$md5" = "x$oldmd5" ]
then
    echo "les md5 sont egaux pas d'action"
    exit 0
else
    echo "les md5 sont differents il faut refactory la base"
fi

# netoyage du repertoire de travail si il n'est pas vide
echo "rm -Rf \"$directory_output\"/"
rm -Rf "$directory_output"/*
# creation du repertoire de travail si il n'existe pas
echo "mkdir -p \"$directory_output\""
mkdir -p "$directory_output"
# move file base fichier
echo mv $path_tmp_file "$directory_output"/
mv $path_tmp_file "$directory_output"/


# execution du script de la base
mysql --user=$user --password=$password < $path_base_wsusscn2

if [ $(table_exists "update_data") = "1" ]; then

    mysql --user="$user" --password="$password" --database="$database" --execute="DROP DATABASE IF EXISTS  update_data"$suffixe"; ALTER TABLE \`$database\`.\`update_data\` RENAME TO  \`$database\`.\`update_data__save\`;"
    # rename table
#     for t in $(echo "show tables from $database;" | mysql -N --user=$user --password=$password | grep "^up_packages_.*"| grep  '$suffixe''$')
#     do
#         droptable $t"$suffixe"
#     done
#     for t in $(echo "show tables from $database;" | mysql -N --user=$user --password=$password | grep "^up_packages_.*"| grep -v '$suffixe''$')
#     do
#         rename_table $t $t"$suffixe"
#     done
fi

# lancement de la generation de la base.
echo "nice -6 python3 /usr/sbin/pulse2-create-base_wsusscn2.py update"
nice -6 python3 /usr/sbin/pulse2-create-base_wsusscn2.py update

mysqldump -p$password $database update_data > $path_base_wsusscn2_dump
