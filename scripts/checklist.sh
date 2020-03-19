#!/bin/bash

day=`date +%d%m%y`
HNAME=`hostname -f`
VERSION="7.6.1810"
OS=`cat /etc/redhat-release | awk '{print $4}'`
KV="$(uname -r)"
OPT_SIZE="$(df -h | grep /opt/repos | awk '{ print $2 }' | sed 's/[^0-9]*//g')"
VAR_SIZE="$(df -h | grep /var/log | awk '{ print $2 }' | sed 's/[^0-9]*//g')"
ROOT_SIZE="$(df -h | grep / | awk '{ print $2 }' | sed 's/[^0-9]*//g' | head -1)"
HN=`hostname`
TZ=`date | awk '{print $5}'`
ETZ=UTC
CIDR=`ip a | grep brd | grep inet| awk '{ print $2 }'`
SE_STATUS=`getenforce`
SWAP=`free -g | grep -i Swap | awk '{print $2}'`
INTERFACE=`ip -4 route get 8.8.8.8 | awk {'print $5'} | tr -d '\n'`
NET_FILE=`echo "/etc/sysconfig/network-scripts/ifcfg-"$INTERFACE`
DHCP_STAT=`cat $NET_FILE | grep BOOTPROTO`
NM_STAT=`systemctl status NetworkManager | grep Active | awk '{print $2}'`
CPU=`nproc --all`
MEM=`free -g | grep -i Mem | awk '{ print $2 }'`
INTERFACE_SPEED=`ethtool $INTERFACE | grep -i Speed | awk '{ print $2}'`
MTU=`ifconfig | grep -i $INTERFACE | awk '{print $4}'`
UPTIME=`cat /proc/uptime | awk '{print $1}'`
UPTIME_INT=`echo ${UPTIME%.*}`
FILE_VALUE=50
IP_FORWARD_VALUE=`cat /proc/sys/net/ipv4/ip_forward`

function green_echo() {
  echo -e "\x1b[1;32m$1\e[0m"
}

function red_echo() {
  echo -e "\x1b[1;31m$1\e[0m"
}


echo "###############################################" > /tmp/Checklist_"$HNAME"_"$day".txt
echo "#################  $HNAME  ####################" >> /tmp/Checklist_"$HNAME"_"$day".txt
echo "###############################################" >> /tmp/Checklist_"$HNAME"_"$day".txt

if [  $UPTIME_INT -gt 21600  ]
then
   green_echo "PASSED - Uptime is more than 6hrs" >> /tmp/Checklist_"$HNAME"_"$day".txt
else
   red_echo "FAILED - Uptime is less than 6hrs" >> /tmp/Checklist_"$HNAME"_"$day".txt
fi

if [ $OS == $VERSION ]
then
	green_echo "PASSED - Linux-OSversion: ${OS} " >>  /tmp/Checklist_"$HNAME"_"$day".txt
else
	red_echo "FAILED - Linux-OSversion:${OS} " >> /tmp/Checklist_"$HNAME"_"$day".txt
fi

green_echo "PASSED - Kernal-version: ${KV} " >> /tmp/Checklist_"$HNAME"_"$day".txt

if [ -z "$OPT_SIZE" ]
then
  red_echo "FAILED - /opt/repos Filesystem NOT FOUND"  >> /tmp/Checklist_"$HNAME"_"$day".txt
else
  if [ `echo $OPT_SIZE` -gt 400 ]
  then
	 green_echo "PASSED - /opt/repos Filesystem size:" ${OPT_SIZE} >> /tmp/Checklist_"$HNAME"_"$day".txt
  else
	red_echo "FAILED - /opt/repos Filesystem size:" ${OPT_SIZE} >> /tmp/Checklist_"$HNAME"_"$day".txt
  fi
fi

if [ $VAR_SIZE -ge $FILE_VALUE  ]
then
        green_echo "PASSED - /var/log Filesystem size: ${VAR_SIZE} " >> /tmp/Checklist_"$HNAME"_"$day".txt
else
        red_echo "FAILED - /var/log Filesystem size: ${VAR_SIZE} " >> /tmp/Checklist_"$HNAME"_"$day".txt
fi

if [ $ROOT_SIZE -ge $FILE_VALUE  ]
then
         green_echo "PASSED - / Filesystem size: ${ROOT_SIZE} " >> /tmp/Checklist_"$HNAME"_"$day".txt
else
        red_echo "FAILED - / Filesystem size: ${ROOT_SIZE} " >> /tmp/Checklist_"$HNAME"_"$day".txt
fi

green_echo "CPU : ${CPU} "  >> /tmp/Checklist_"$HNAME"_"$day".txt
green_echo "MEMORY in GB : ${MEM} " >> /tmp/Checklist_"$HNAME"_"$day".txt
green_echo "Interface Link MTU is : ${MTU} "  >> /tmp/Checklist_"$HNAME"_"$day".txt

if [  $SWAP -eq 0 ]
then
    green_echo "PASSED - SWAP is off" >> /tmp/Checklist_"$HNAME"_"$day".txt
else
    red_echo "FAILED - SWAP is Available" >> /tmp/Checklist_"$HNAME"_"$day".txt
fi

if [  $SE_STATUS == "Disabled" -o  $SE_STATUS == "Permissive" ]
then
	green_echo "PASSED - Selinux off" >> /tmp/Checklist_"$HNAME"_"$day".txt
else
    red_echo "FAILED - Selinux is Enabled " >> /tmp/Checklist_"$HNAME"_"$day".txt
fi

systemctl status firewalld.service
if [ $? -eq 0 ]
then
	red_echo "FAILED - Firewalld service is Active" >> /tmp/Checklist_"$HNAME"_"$day".txt
else
    green_echo "PASSED - Firewalld service Stoped" >> /tmp/Checklist_"$HNAME"_"$day".txt
fi

systemctl status ntpd.service
if [ $? -eq 0 ]
then
     green_echo "PASSED - NTPD service is Configured" >> /tmp/Checklist_"$HNAME"_"$day".txt
else
     red_echo "FAILED - NTPD is not Configured" >> /tmp/Checklist_"$HNAME"_"$day".txt
fi

if [ $IP_FORWARD_VALUE -eq 1 ]
then
   green_echo "PASSED - IP Forwarding is Enabled" >> /tmp/Checklist_"$HNAME"_"$day".txt
else
   red_echo "FAILED - IP Forwarding is Disable" >> /tmp/Checklist_"$HNAME"_"$day".txt
fi
