#!/bin/bash

bench init \
--frappe-path /tmp/frappe \
--skip-redis-config-generation \
--ignore-exist \
--skip-redis-config-generation \
frappe-bench

cd frappe-bench

mysql -u root -h 127.0.0.1 -p123 -e "CREATE DATABASE test_frappe";
mysql -u root -h 127.0.0.1 -p123 -e "CREATE USER 'test_frappe'@'localhost' IDENTIFIED BY 'test_frappe'";
mysql -u root -h 127.0.0.1 -p123 -e "GRANT ALL PRIVILEGES ON \`test_frappe\`.* TO 'test_frappe'@'localhost'";
mysql -u root -h 127.0.0.1 -p123 -e "UPDATE mysql.user SET Password=PASSWORD('circleci') WHERE User='root'";
mysql -u root -h 127.0.0.1 -p123 -e "FLUSH PRIVILEGES";

yes | cp ./apps/frappe/.circleci/common_site_config.json ./sites/common_site_config.json # Overwrite
mkdir ./sites/test_site
cp ./apps/frappe/.circleci/site_config.json ./sites/test_site/site_config.json

echo '127.0.0.1   test_site' | sudo tee -a /etc/hosts
bench --site test_site reinstall --yes
bench build --app frappe