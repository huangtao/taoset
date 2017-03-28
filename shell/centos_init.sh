#!/bin/sh

###################################################################################################################
# postgresql

# 查看已安装的包
# rpm -qa|grep postgres

# 卸载postgresql
# rpm -e postgresql-server-8.4.20-6.el6.x86_64
# rpm -e postgresql-8.4.20-6.el6.x86_64
# rpm -e postgresql-libs-8.4.20-6.el6.x86_64

# 下载postgresql
wget https://yum.postgresql.org/9.6/redhat/rhel-6-x86_64/postgresql96-9.6.2-2PGDG.rhel6.x86_64.rpm
wget https://yum.postgresql.org/9.6/redhat/rhel-6-x86_64/postgresql96-contrib-9.6.2-2PGDG.rhel6.x86_64.rpm
wget https://yum.postgresql.org/9.6/redhat/rhel-6-x86_64/postgresql96-libs-9.6.2-2PGDG.rhel6.x86_64.rpm
wget https://yum.postgresql.org/9.6/redhat/rhel-6-x86_64/postgresql96-server-9.6.2-2PGDG.rhel6.x86_64.rpm

# 安装
# 注意:postgresql-contrib依赖libxslt
yum install libxslt
rpm -ivh postgresql96-libs-9.6.2-2PGDG.rhel6.x86_64.rpm
rpm -ivh postgresql96-9.6.2-2PGDG.rhel6.x86_64.rpm
rpm -ivh postgresql96-server-9.6.2-2PGDG.rhel6.x86_64.rpm
rpm -ivh postgresql96-contrib-9.6.2-2PGDG.rhel6.x86_64.rpm
# 初始化数据库
service postgresql-9.6 initdb
# 启动服务
service postgresql-9.6 start
# 开机启动
chkconfig postgresql-9.6 on

# 配置postgresql
# 修改默认创建的postgres数据库用户连接密码(默认为空密码)
# su - postgres
# psql
# ALTER USER postgres WITH PASSWORD 'postgres';
# select * from pg_shadow;
# exit

# 修改postgres系统用户密码
# passwd postgres 

# 配置postgresql远程访问(应用服务器访问数据库服务器时配置)
# vi /var/lib/pgsql/9.6/data/postgresql.chkconf
# 将listen_addresses = 'localhost'改成listen_addresses = '*'并去掉注释
# vi /var/lib/pgsql/9.6/data/pg_hba.conf
# 允许所有IP地址访问(密码md5加密),测试可以生产环境不建议配置
# host all all 0.0.0.0/0 md5
# 只允许指定的IP访问
# host all all 60.190.138.22/32 md5


#############################################################################################
# Node.js
curl --silent --location https://rpm.nodesource.com/setup_6.x | bash -
yum -y install nodejs
npm install express -g