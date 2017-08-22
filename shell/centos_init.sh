#!/bin/sh

###########################################################################################
# 防火墙配置
# yum install iptables
# apt-get install iptables
echo "seting firewall..."
# 删除现有规则
iptables -F
iptables -X
iptables -Z
# 配置默认策略(能出不能进)
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# ssh
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
# 80
#iptables -A INPUT -p tcp --dport 80 -j ACCEPT
# ftp 20,21
#iptables -A INPUT -p tcp --dport 20 -j ACCEPT
#iptables -A INPUT -p tcp --dport 21 -j ACCEPT

# Gate服务器
iptables -A INPUT -p tcp --dport 8600 -j ACCEPT
iptables -A INPUT -p tcp --dport 8601 -j ACCEPT
# 代理服务器
iptables -A INPUT -p tcp --dport 8602 -j ACCEPT
# 游戏服务器
iptables -A INPUT -p tcp --dport 8610 -j ACCEPT

# 屏蔽指定IP
#iptables -I INPUT -s 60.190.238.24 -j DROP
# 屏蔽整个段
#iptables -I INPUT -s 123.0.0.0/8 -j DROP

# 允许本地回环
iptables -A INPUT -s 127.0.0.1 -d 127.0.0.1 -j ACCEPT

# 打开 syncookie(轻量级预防DOS攻击)
#sysctl -w net.ipv4.tcp_syncookies=1 &>/dev/null

# 开机自动启动防火墙
chkconfig iptables on

# 保存配置
service iptables save

#############################################################################################
yum install wget


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
# \q
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

# 注意:如果连接服务器返回ident authentication failed for user 'postgres'
# 由于连接127.0.0.1使用的是ident认证方式,所以将连接地址改为公网IP即可


#############################################################################################
# Node.js
curl --silent --location https://rpm.nodesource.com/setup_6.x | bash -
yum -y install nodejs
npm install express -g

# 关于pm2
# 启动服务器
# pm2 start app.js
# pm2 start app.js --name 'myname'

# 指定端口启动express
# PORT=80 pm2 start ./bin/www --name www

# 将应用列表保存用于pm2启动时自动启动
# pm2 save

# 开机自动启动(放最后)
# pm2 startup