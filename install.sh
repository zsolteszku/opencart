#!/bin/bash

cd upload
if [[ ! -f config.php || ! -f admin/config.php ]]; then
	echo "Not correctly configured yet!"
    rm config.php
    rm admin/config.php
    cp config-dist.php config.php
    cp admin/config-dist.php admin/config.php
else
	echo "Correctly configured. So deleting install directory"
	rm -rf install
fi
mkdir system/cache
chmod -R 0777 system/cache/
mkdir system/logs/
chmod 0777 system/logs/
mkdir system/download/
chmod 0777 system/download/
mkdir system/upload
chmod 0777 system/upload/
chmod 0777 image/
mkdir image/cache
chmod 0777 image/cache/
chmod 0777 image/catalog/
chmod 0777 config.php
chmod 0777 admin/config.php
chmod -R 0777 ./
