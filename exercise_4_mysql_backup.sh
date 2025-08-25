#!/bin/bash
cd /home/$1/backups/
mkdir mysql
suffix=$(date +%y%m%d)
MYSQL="$(which mysql)"
databases="$($MYSQL -u $1 -p$2 -Bse ‘show databases’)"
for database in $databases
do
  echo "Processing database $database"
  mysqldump –opt -u$1 -p$2 ${database} > mysql/${database}.$suffix.sql
done
tar -cf archives/mysql_backup.$suffix.tar mysql/*
rm -r mysql/
@psanogo
Comment
