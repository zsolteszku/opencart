#!/bin/sh

git pull
cd upload
mkdir system/cache
chmod 0777 system/cache/
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
