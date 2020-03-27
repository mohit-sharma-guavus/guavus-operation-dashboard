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
date_time=`date "+%Y-%m-%d_%H:%M"`

#function green_echo() {
#  echo -e "\x1b[1;32m$1\e[0m"
#}

#function red_echo() {
#  echo -e "\x1b[1;31m$1\e[0m"
#}

#> /tmp/Checklist_PASSED.txt
#> /tmp/Checklist_FAILED.txt
> /tmp/Checklist_"$HNAME"_"$day".txt
echo "$HNAME" >> /tmp/Checklist_"$HNAME"_"$day".txt
echo "$date_time" >> /tmp/Checklist_"$HNAME"_"$day".txt


if [  $UPTIME_INT -gt 21600  ]
then
   echo "PASSED - Uptime > 6hrs" >> /tmp/Checklist_"$HNAME"_"$day".txt
else
   echo "FAILED - Uptime < 6hrs" >> /tmp/Checklist_"$HNAME"_"$day".txt
fi

if [ $OS == $VERSION ]
then
	echo "PASSED -  ${OS} " >>  /tmp/Checklist_"$HNAME"_"$day".txt
else
	echo "FAILED -  ${OS} " >> /tmp/Checklist_"$HNAME"_"$day".txt
fi

echo "PASSED -  ${KV} " >> /tmp/Checklist_"$HNAME"_"$day".txt

if [ -z "$OPT_SIZE" ]
then
  echo "FAILED - /opt/repos FS NOT FOUND"  >> /tmp/Checklist_"$HNAME"_"$day".txt
else
  if [ `echo $OPT_SIZE` -gt 400 ]
  then
	  echo "PASSED - /opt/repos FS size:" ${OPT_SIZE} >> /tmp/Checklist_"$HNAME"_"$day".txt
  else
	  echo "FAILED - /opt/repos FS size:" ${OPT_SIZE} >> /tmp/Checklist_"$HNAME"_"$day".txt
  fi
fi

if [ $VAR_SIZE -ge $FILE_VALUE  ]
then
      echo "PASSED - /var/log FS size: ${VAR_SIZE} " >> /tmp/Checklist_"$HNAME"_"$day".txt
else
      echo "FAILED - /var/log FS size: ${VAR_SIZE} " >> /tmp/Checklist_"$HNAME"_"$day".txt
fi

if [ $ROOT_SIZE -ge $FILE_VALUE  ]
then
      echo "PASSED - / FS size: ${ROOT_SIZE} " >> /tmp/Checklist_"$HNAME"_"$day".txt
else
      echo "FAILED - / FS size: ${ROOT_SIZE} " >> /tmp/Checklist_"$HNAME"_"$day".txt
fi

echo "CPU : ${CPU} "  >> /tmp/Checklist_"$HNAME"_"$day".txt
echo "MEMORY : ${MEM} " >> /tmp/Checklist_"$HNAME"_"$day".txt
echo "Interface MTU is : ${MTU} "  >> /tmp/Checklist_"$HNAME"_"$day".txt

if [  $SWAP -eq 0 ]
then
    echo "PASSED - SWAP off" >> /tmp/Checklist_"$HNAME"_"$day".txt
else
    echo "FAILED - SWAP on" >> /tmp/Checklist_"$HNAME"_"$day".txt
fi

if [  $SE_STATUS == "Disabled" -o  $SE_STATUS == "Permissive" ]
then
	echo "PASSED - Selinux Disabled" >> /tmp/Checklist_"$HNAME"_"$day".txt
else
  echo "FAILED - Selinux Enabled " >> /tmp/Checklist_"$HNAME"_"$day".txt
fi

systemctl status firewalld.service
if [ $? -eq 0 ]
then
	echo "FAILED - Firewalld Active" >> /tmp/Checklist_"$HNAME"_"$day".txt
else
  echo "PASSED - Firewalld Stopped" >> /tmp/Checklist_"$HNAME"_"$day".txt
fi

systemctl status ntpd.service
if [ $? -eq 0 ]
then
  echo "PASSED - NTPD Configured" >> /tmp/Checklist_"$HNAME"_"$day".txt
else
  echo "FAILED - NTPD not Configured" >> /tmp/Checklist_"$HNAME"_"$day".txt
fi

if [ $IP_FORWARD_VALUE -eq 1 ]
then
  echo "PASSED - IP Forwarding Enabled" >> /tmp/Checklist_"$HNAME"_"$day".txt
else
  echo "FAILED - IP Forwarding Disable" >> /tmp/Checklist_"$HNAME"_"$day".txt
fi



#echo "######################################" > /tmp/Checklist_"$HNAME"_"$day".txt
#echo "$HNAME" >> /tmp/Checklist_"$HNAME"_"$day".txt
#echo "######################################" >> /tmp/Checklist_"$HNAME"_"$day".txt
#echo "$date_time" >> /tmp/Checklist_"$HNAME"_"$day".txt
#echo "########  PASSED CHECKS   ############" >> /tmp/Checklist_"$HNAME"_"$day".txt
#cat /tmp/Checklist_PASSED.txt >> /tmp/Checklist_"$HNAME"_"$day".txt
#echo "######### FAILED CHECKS   ############" >> /tmp/Checklist_"$HNAME"_"$day".txt
#cat /tmp/Checklist_FAILED.txt >> /tmp/Checklist_"$HNAME"_"$day".txt
#echo "#######################################" >> /tmp/Checklist_"$HNAME"_"$day".txt