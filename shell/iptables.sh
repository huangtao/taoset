#!/bin/sh

###########################################################################################
# 防火墙配置
# 以centos为准
#

# yum install iptables
# apt-get install iptables

echo "seting firewall..."
# 查看规则
# iptables -L
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
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
# https
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
# ftp 20,21
#iptables -A INPUT -p tcp --dport 20 -j ACCEPT
#iptables -A INPUT -p tcp --dport 21 -j ACCEPT

# dns(服务器有http请求需要解析dsn时需要打开)
iptables -A INPUT -p udp --sport 53 -j ACCEPT

# Gate服务器
iptables -A INPUT -p tcp --dport 8600 -j ACCEPT
iptables -A INPUT -p tcp --dport 8601 -j ACCEPT
# 代理服务器
iptables -A INPUT -p tcp --dport 8602 -j ACCEPT
# 游戏服务器
iptables -A INPUT -p tcp --dport 8610 -j ACCEPT
# h5服务器
iptables -A INPUT -p tcp --dport 3000 -j ACCEPT

# postgres
# 只允许指定地址
#iptables -A INPUT -p tcp --dport 5432 -s 42.120.18.183 -j ACCEPT

# 允许本地回环
iptables -A INPUT -s 127.0.0.1 -d 127.0.0.1 -j ACCEPT

# 屏蔽指定IP
iptables -I INPUT -s 124.239.180.102 -j DROP
# 屏蔽整个段
#iptables -I INPUT -s 123.0.0.0/8 -j DROP

# 打开 syncookie(轻量级预防DOS攻击)
#sysctl -w net.ipv4.tcp_syncookies=1 &>/dev/null

# 开机自动启动防火墙
chkconfig iptables on

# 保存配置
service iptables save
